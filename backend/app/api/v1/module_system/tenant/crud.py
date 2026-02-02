from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.module_system.tenant.model import TenantModel
from app.api.v1.module_system.tenant.schema import (
    TenantCreateSchema,
    TenantUpdateSchema,
)
from app.common.response import paginate_response


class TenantCrud:
    """租户数据操作类"""

    @staticmethod
    async def create(db: AsyncSession, obj_in: TenantCreateSchema) -> TenantModel:
        """
        创建租户

        Args:
            db: 数据库会话
            obj_in: 创建数据

        Returns:
            创建的租户对象
        """
        db_obj = TenantModel(**obj_in.model_dump())
        db.add(db_obj)
        await db.flush()
        return db_obj

    @staticmethod
    async def get_by_id(db: AsyncSession, tenant_id: int) -> TenantModel | None:
        """
        根据ID获取租户

        Args:
            db: 数据库会话
            tenant_id: 租户ID

        Returns:
            租户对象或None
        """
        sql = select(TenantModel).where(TenantModel.id == tenant_id)
        result = await db.execute(sql)
        return result.scalars().first()

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> TenantModel | None:
        """
        根据编码获取租户

        Args:
            db: 数据库会话
            code: 租户编码

        Returns:
            租户对象或None
        """
        sql = select(TenantModel).where(TenantModel.code == code)
        result = await db.execute(sql)
        return result.scalars().first()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        name: str | None = None,
        code: str | None = None,
        tenant_type: int | None = None,
        is_active: bool | None = None,
        status: str | None = None,
    ) -> list[TenantModel]:
        """
        获取所有租户（不分页）

        Args:
            db: 数据库会话
            name: 租户名称（模糊查询）
            code: 租户编码（模糊查询）
            tenant_type: 租户类型
            is_active: 是否启用
            status: 状态

        Returns:
            租户列表
        """
        sql = select(TenantModel)

        # 构建查询条件
        if name:
            sql = sql.where(TenantModel.name.like(f"%{name}%"))
        if code:
            sql = sql.where(TenantModel.code.like(f"%{code}%"))
        if tenant_type is not None:
            sql = sql.where(TenantModel.tenant_type == tenant_type)
        if is_active is not None:
            sql = sql.where(TenantModel.is_active == is_active)
        if status:
            sql = sql.where(TenantModel.status == status)

        # 按创建时间倒序
        sql = sql.order_by(TenantModel.created_time.desc())

        result = await db.execute(sql)
        return list(result.scalars().all())

    @staticmethod
    async def get_list(
        db: AsyncSession,
        page: int = 1,
        size: int = 10,
        name: str | None = None,
        code: str | None = None,
        tenant_type: int | None = None,
        is_active: bool | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        """
        获取租户列表（分页）

        Args:
            db: 数据库会话
            page: 页码
            size: 每页数量
            name: 租户名称（模糊查询）
            code: 租户编码（模糊查询）
            tenant_type: 租户类型
            is_active: 是否启用
            status: 状态

        Returns:
            分页结果
        """
        sql = select(TenantModel)

        # 构建查询条件
        if name:
            sql = sql.where(TenantModel.name.like(f"%{name}%"))
        if code:
            sql = sql.where(TenantModel.code.like(f"%{code}%"))
        if tenant_type is not None:
            sql = sql.where(TenantModel.tenant_type == tenant_type)
        if is_active is not None:
            sql = sql.where(TenantModel.is_active == is_active)
        if status:
            sql = sql.where(TenantModel.status == status)

        # 按创建时间倒序
        sql = sql.order_by(TenantModel.created_time.desc())

        return await paginate_response(db=db, sql=sql, page=page, size=size)

    @staticmethod
    async def update(
        db: AsyncSession, db_obj: TenantModel, obj_in: TenantUpdateSchema
    ) -> TenantModel:
        """
        更新租户

        Args:
            db: 数据库会话
            db_obj: 数据库中的租户对象
            obj_in: 更新数据

        Returns:
            更新后的租户对象
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await db.flush()
        return db_obj

    @staticmethod
    async def delete(db: AsyncSession, db_obj: TenantModel) -> None:
        """
        删除租户（软删除）

        Args:
            db: 数据库会话
            db_obj: 租户对象
        """
        # 软删除：将状态设置为1（禁用）
        db_obj.status = "1"
        await db.flush()

    @staticmethod
    async def check_code_exists(db: AsyncSession, code: str, exclude_id: int | None = None) -> bool:
        """
        检查租户编码是否存在

        Args:
            db: 数据库会话
            code: 租户编码
            exclude_id: 排除的租户ID（用于更新时检查）

        Returns:
            是否存在
        """
        sql = select(TenantModel.id).where(TenantModel.code == code)
        if exclude_id:
            sql = sql.where(TenantModel.id != exclude_id)
        result = await db.execute(sql)
        return result.scalars().first() is not None

    @staticmethod
    async def has_related_users(db: AsyncSession, tenant_id: int) -> bool:
        """
        检查租户是否有关联的用户

        Args:
            db: 数据库会话
            tenant_id: 租户ID

        Returns:
            是否有关联用户
        """
        from app.api.v1.module_system.user.model import UserModel

        sql = select(UserModel.id).where(UserModel.tenant_id == tenant_id).limit(1)
        result = await db.execute(sql)
        return result.scalars().first() is not None

    @staticmethod
    async def has_related_depts(db: AsyncSession, tenant_id: int) -> bool:
        """
        检查租户是否有关联的部门

        Args:
            db: 数据库会话
            tenant_id: 租户ID

        Returns:
            是否有关联部门
        """
        from app.api.v1.module_system.dept.model import DeptModel

        sql = select(DeptModel.id).where(DeptModel.tenant_id == tenant_id).limit(1)
        result = await db.execute(sql)
        return result.scalars().first() is not None

    @staticmethod
    async def has_related_roles(db: AsyncSession, tenant_id: int) -> bool:
        """
        检查租户是否有关联的角色

        Args:
            db: 数据库会话
            tenant_id: 租户ID

        Returns:
            是否有关联角色
        """
        from app.api.v1.module_system.role.model import RoleModel

        sql = select(RoleModel.id).where(RoleModel.tenant_id == tenant_id).limit(1)
        result = await db.execute(sql)
        return result.scalars().first() is not None
