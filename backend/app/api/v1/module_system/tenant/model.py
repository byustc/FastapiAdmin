from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin

if TYPE_CHECKING:
    from app.api.v1.module_system.dept.model import DeptModel
    from app.api.v1.module_system.role.model import RoleModel
    from app.api.v1.module_system.user.model import UserModel


class TenantModel(ModelMixin, UserMixin):
    """
    租户模型（平级架构）

    设计要点：
    - 平级架构，无 parent_id，不支持租户层级
    - code 字段唯一索引，用于快速查询
    - is_active 控制租户是否可用
    - tenant_type 可扩展，支持不同类型的组织机构
    """

    __tablename__: str = "sys_tenant"
    __table_args__: dict[str, str] = {"comment": "租户表"}
    __loader_options__: list[str] = ["created_by", "updated_by"]

    # ========== 基础信息 ==========
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="租户名称"
    )
    code: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True, index=True, comment="租户编码"
    )
    short_name: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="租户简称"
    )
    logo: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="租户Logo URL"
    )

    # ========== 租户类型 ==========
    tenant_type: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="租户类型(0:企业 1:政府 2:学校 3:医院 4:其他)",
    )

    # ========== 联系信息 ==========
    contact_person: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="联系人"
    )
    contact_phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="联系电话"
    )
    contact_email: Mapped[str | None] = mapped_column(
        String(128), nullable=True, comment="联系邮箱"
    )
    address: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="地址"
    )

    # ========== 状态管理 ==========
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="是否启用"
    )

    # ========== 关联关系 ==========
    users: Mapped[list["UserModel"]] = relationship(
        back_populates="tenant",
        foreign_keys="UserModel.tenant_id",
        lazy="selectin",
    )
    depts: Mapped[list["DeptModel"]] = relationship(
        back_populates="tenant",
        foreign_keys="DeptModel.tenant_id",
        lazy="selectin",
    )
    roles: Mapped[list["RoleModel"]] = relationship(
        back_populates="tenant",
        foreign_keys="RoleModel.tenant_id",
        lazy="selectin",
    )
