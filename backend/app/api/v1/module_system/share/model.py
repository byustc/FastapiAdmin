from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base_model import ModelMixin, UserMixin

if TYPE_CHECKING:
    from app.api.v1.module_system.tenant.model import TenantModel


class DataShareModel(ModelMixin, UserMixin):
    """
    数据分享模型

    支持跨租户数据分享，区分查看和编辑权限
    分享无需审批，直接生效

    设计要点：
    - resource_type + resource_id 唯一标识一个资源
    - share_type 区分权限类型（1-仅查看 2-查看和编辑）
    - status 控制分享是否生效（0-生效 1-失效）
    - expire_time 支持设置过期时间（NULL=永久有效）
    """

    __tablename__: str = "sys_data_share"
    __table_args__: dict[str, str] = {"comment": "数据分享表"}
    __loader_options__: list[str] = ["target_tenant", "created_by", "updated_by"]

    # ========== 资源标识 ==========
    resource_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="资源类型(表名)",
    )
    resource_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="资源ID",
    )

    # ========== 分享目标 ==========
    target_tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sys_tenant.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
        comment="目标租户ID",
    )

    # ========== 权限类型 ==========
    share_type: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="分享类型(1:仅查看 2:查看和编辑)",
    )

    # ========== 状态管理 ==========
    status: Mapped[str] = mapped_column(
        String(10),
        default="0",
        nullable=False,
        comment="状态(0:生效 1:失效)",
    )

    # ========== 过期时间 ==========
    expire_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="过期时间(NULL表示永久)",
    )

    # ========== 备注 ==========
    remark: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="分享说明",
    )

    # ========== 关联关系 ==========
    target_tenant: Mapped["TenantModel"] = relationship(
        foreign_keys=[target_tenant_id],
        lazy="selectin",
    )
