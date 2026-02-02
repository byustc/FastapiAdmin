from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.module_system.auth.schema import AuthSchema
from app.core.base_model import MappedBase
from app.api.v1.module_system.share.model import DataShareModel
from app.api.v1.module_system.share.schema import (
    DataCopySchema,
    DataCopyResponseSchema,
    DataShareCreateSchema,
    DataShareListSchema,
)
from app.core.exceptions import CustomException
from app.common.response import paginate_response
from app.utils.common_util import uuid4_str


class ShareService:
    """数据分享和复制业务逻辑类"""

    # 支持复制的表名到模型类的映射
    MODEL_MAPPING: dict[str, str] = {
        "sys_user": "app.api.v1.module_system.user.model:UserModel",
        "sys_dept": "app.api.v1.module_system.dept.model:DeptModel",
        "sys_role": "app.api.v1.module_system.role.model:RoleModel",
        # 可根据需要添加更多表
    }

    @staticmethod
    async def create_share_service(obj_in: DataShareCreateSchema, auth: AuthSchema) -> DataShareModel:
        """
        创建数据分享

        Args:
            obj_in: 分享数据
            auth: 认证信息

        Returns:
            创建的分享对象

        Raises:
            CustomException: 目标租户不存在
        """
        from app.api.v1.module_system.tenant.model import TenantModel
        from app.api.v1.module_system.tenant.crud import TenantCrud

        # 检查目标租户是否存在
        target_tenant = await TenantCrud.get_by_id(db=auth.db, tenant_id=obj_in.target_tenant_id)
        if not target_tenant:
            raise CustomException(msg="目标租户不存在")

        # 检查目标租户是否启用
        if not target_tenant.is_active:
            raise CustomException(msg="目标租户已禁用")

        # 创建分享记录
        db_obj = DataShareModel(**obj_in.model_dump())
        db_obj.status = "0"  # 默认生效
        auth.db.add(db_obj)
        await auth.db.flush()

        # 设置创建者
        if auth.user:
            db_obj.created_id = auth.user.id
            db_obj.updated_id = auth.user.id

        return db_obj

    @staticmethod
    async def revoke_share_service(share_id: int, auth: AuthSchema) -> None:
        """
        撤销数据分享（软删除）

        Args:
            share_id: 分享ID
            auth: 认证信息

        Raises:
            CustomException: 分享记录不存在
        """
        sql = select(DataShareModel).where(DataShareModel.id == share_id)
        result = await auth.db.execute(sql)
        db_obj = result.scalars().first()

        if not db_obj:
            raise CustomException(msg="分享记录不存在")

        # 软删除：将状态设置为1（失效）
        db_obj.status = "1"
        if auth.user:
            db_obj.updated_id = auth.user.id
        await auth.db.flush()

    @staticmethod
    async def list_service(obj_in: DataShareListSchema, auth: AuthSchema) -> dict:
        """
        获取分享列表（分页）

        Args:
            obj_in: 查询参数
            auth: 认证信息

        Returns:
            分页结果
        """
        sql = select(DataShareModel)

        # 构建查询条件
        if obj_in.resource_type:
            sql = sql.where(DataShareModel.resource_type == obj_in.resource_type)
        if obj_in.target_tenant_id:
            sql = sql.where(DataShareModel.target_tenant_id == obj_in.target_tenant_id)
        if obj_in.share_type:
            sql = sql.where(DataShareModel.share_type == obj_in.share_type)
        if obj_in.status:
            sql = sql.where(DataShareModel.status == obj_in.status)

        # 按创建时间倒序
        sql = sql.order_by(DataShareModel.created_time.desc())

        return await paginate_response(db=auth.db, sql=sql, page=obj_in.page, size=obj_in.size)

    @staticmethod
    async def copy_data_service(
        obj_in: DataCopySchema,
        auth: AuthSchema,
    ) -> DataCopyResponseSchema:
        """
        复制数据到目标租户

        说明：
        - 仅复制主表数据，不复制关联数据
        - 复制后的数据完全独立，与源数据无关联
        - 生成新的 UUID 和 ID
        - tenant_id 设置为目标租户
        - created_id 设置为当前操作者

        Args:
            obj_in: 复制请求
            auth: 认证信息

        Returns:
            复制结果

        Raises:
            CustomException: 不支持的资源类型
            CustomException: 未找到要复制的数据
        """
        # 1. 动态导入模型类
        model_class = ShareService._get_model_by_table_name(obj_in.resource_type)

        # 2. 查询源数据
        from sqlalchemy import select

        sql = select(model_class).where(model_class.id.in_(obj_in.resource_ids))
        result = await auth.db.execute(sql)
        source_objects = result.scalars().all()

        if not source_objects:
            raise CustomException(msg="未找到要复制的数据")

        # 3. 逐个复制数据
        copied_count = 0
        id_mapping = {}

        for obj in source_objects:
            # 克隆对象
            new_obj = ShareService._clone_object(
                obj=obj,
                target_tenant_id=obj_in.target_tenant_id,
                auth=auth,
            )

            auth.db.add(new_obj)
            await auth.db.flush()  # 获取新ID

            id_mapping[obj.id] = new_obj.id
            copied_count += 1

        return DataCopyResponseSchema(
            copied_count=copied_count,
            target_tenant_id=obj_in.target_tenant_id,
            id_mapping=id_mapping,
        )

    @staticmethod
    def _clone_object(
        obj: MappedBase,
        target_tenant_id: int,
        auth: AuthSchema,
    ) -> MappedBase:
        """
        克隆对象（深拷贝）

        跳过字段：
        - 主键（id）
        - 只读字段（created_time, updated_time）

        覆盖字段：
        - uuid → 生成新的UUID
        - tenant_id → 目标租户ID
        - created_id → 当前操作者
        """
        from sqlalchemy import inspect

        mapper = inspect(obj)
        new_obj = obj.__class__()

        for column in mapper.columns:
            # 跳过主键
            if column.primary_key:
                continue

            # 跳过只读字段
            if column.name in ["created_time", "updated_time"]:
                continue

            # 获取原值
            value = getattr(obj, column.name)

            # 覆盖特定字段
            if column.name == "tenant_id":
                setattr(new_obj, column.name, target_tenant_id)
            elif column.name == "uuid":
                setattr(new_obj, column.name, uuid4_str())
            elif column.name in ["created_id", "updated_id"] and auth.user:
                setattr(new_obj, column.name, auth.user.id)
            else:
                # 保留其他字段值
                setattr(new_obj, column.name, value)

        return new_obj

    @staticmethod
    def _get_model_by_table_name(table_name: str) -> type[MappedBase]:
        """
        根据表名动态获取模型类

        Args:
            table_name: 表名

        Returns:
            模型类

        Raises:
            CustomException: 不支持的资源类型
        """
        if table_name not in ShareService.MODEL_MAPPING:
            raise CustomException(msg=f"不支持的资源类型: {table_name}")

        # 动态导入
        import_path = ShareService.MODEL_MAPPING[table_name]
        module_path, class_name = import_path.split(":")

        from importlib import import_module

        module = import_module(module_path)
        return getattr(module, class_name)
