from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_system.tenant.crud import TenantCrud
from app.api.v1.module_system.tenant.model import TenantModel
from app.api.v1.module_system.tenant.schema import (
    TenantCreateSchema,
    TenantListSchema,
    TenantUpdateSchema,
)
from app.core.exceptions import CustomException


class TenantService:
    """租户业务逻辑类"""

    @staticmethod
    async def create_service(obj_in: TenantCreateSchema, auth: AuthSchema) -> TenantModel:
        """
        创建租户

        Args:
            obj_in: 创建数据
            auth: 认证信息

        Returns:
            创建的租户对象

        Raises:
            CustomException: 租户编码已存在
        """
        # 检查租户编码是否已存在
        if await TenantCrud.check_code_exists(db=auth.db, code=obj_in.code):
            raise CustomException(msg=f"租户编码 '{obj_in.code}' 已存在")

        # 创建租户
        db_obj = await TenantCrud.create(db=auth.db, obj_in=obj_in)

        # 设置创建者
        if auth.user:
            db_obj.created_id = auth.user.id
            db_obj.updated_id = auth.user.id

        return db_obj

    @staticmethod
    async def update_service(obj_in: TenantUpdateSchema, auth: AuthSchema) -> TenantModel:
        """
        更新租户

        Args:
            obj_in: 更新数据
            auth: 认证信息

        Returns:
            更新后的租户对象

        Raises:
            CustomException: 租户不存在
            CustomException: 租户编码已存在
        """
        # 获取租户
        db_obj = await TenantCrud.get_by_id(db=auth.db, tenant_id=obj_in.id)
        if not db_obj:
            raise CustomException(msg="租户不存在")

        # 如果更新编码，检查是否已存在
        if obj_in.code and obj_in.code != db_obj.code:
            if await TenantCrud.check_code_exists(
                db=auth.db, code=obj_in.code, exclude_id=obj_in.id
            ):
                raise CustomException(msg=f"租户编码 '{obj_in.code}' 已存在")

        # 更新租户
        db_obj = await TenantCrud.update(db=auth.db, db_obj=db_obj, obj_in=obj_in)

        # 设置更新者
        if auth.user:
            db_obj.updated_id = auth.user.id

        return db_obj

    @staticmethod
    async def delete_service(ids: list[int], auth: AuthSchema) -> int:
        """
        删除租户（软删除）

        Args:
            ids: 租户ID列表
            auth: 认证信息

        Returns:
            删除数量

        Raises:
            CustomException: 租户有关联数据
        """
        delete_count = 0

        for tenant_id in ids:
            # 获取租户
            db_obj = await TenantCrud.get_by_id(db=auth.db, tenant_id=tenant_id)
            if not db_obj:
                continue

            # 检查是否有关联数据
            has_users = await TenantCrud.has_related_users(db=auth.db, tenant_id=tenant_id)
            has_depts = await TenantCrud.has_related_depts(db=auth.db, tenant_id=tenant_id)
            has_roles = await TenantCrud.has_related_roles(db=auth.db, tenant_id=tenant_id)

            if has_users or has_depts or has_roles:
                raise CustomException(
                    msg=f"租户 '{db_obj.name}' 存在关联数据（用户/部门/角色），无法删除"
                )

            # 软删除
            await TenantCrud.delete(db=auth.db, db_obj=db_obj)
            delete_count += 1

        return delete_count

    @staticmethod
    async def detail_service(tenant_id: int, auth: AuthSchema) -> TenantModel:
        """
        获取租户详情

        Args:
            tenant_id: 租户ID
            auth: 认证信息

        Returns:
            租户对象

        Raises:
            CustomException: 租户不存在
        """
        db_obj = await TenantCrud.get_by_id(db=auth.db, tenant_id=tenant_id)
        if not db_obj:
            raise CustomException(msg="租户不存在")
        return db_obj

    @staticmethod
    async def list_service(obj_in: TenantListSchema, auth: AuthSchema) -> dict:
        """
        获取租户列表（分页）

        Args:
            obj_in: 查询参数
            auth: 认证信息

        Returns:
            分页结果
        """
        return await TenantCrud.get_list(
            db=auth.db,
            page=obj_in.page,
            size=obj_in.size,
            name=obj_in.name,
            code=obj_in.code,
            tenant_type=obj_in.tenant_type,
            is_active=obj_in.is_active,
            status=obj_in.status,
        )

    @staticmethod
    async def all_service(auth: AuthSchema, **kwargs) -> list[TenantModel]:
        """
        获取所有租户（不分页，用于下拉选择）

        Args:
            auth: 认证信息
            **kwargs: 额外过滤参数

        Returns:
            租户列表
        """
        return await TenantCrud.get_all(
            db=auth.db,
            name=kwargs.get("name"),
            code=kwargs.get("code"),
            tenant_type=kwargs.get("tenant_type"),
            is_active=kwargs.get("is_active", True),  # 默认只返回启用的租户
            status=kwargs.get("status"),
        )
