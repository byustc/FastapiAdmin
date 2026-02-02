from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DataShareCreateSchema(BaseModel):
    """数据分享创建模型"""
    resource_type: str = Field(..., min_length=1, max_length=64, description="资源类型(表名)")
    resource_id: int = Field(..., description="资源ID")
    target_tenant_id: int = Field(..., description="目标租户ID")
    share_type: Literal[1, 2] = Field(
        default=1, description="分享类型(1:仅查看 2:查看和编辑)"
    )
    expire_time: datetime | None = Field(None, description="过期时间(NULL表示永久)")
    remark: str | None = Field(None, max_length=500, description="分享说明")


class DataShareOutSchema(BaseModel):
    """数据分享输出模型"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    resource_type: str
    resource_id: int
    target_tenant_id: int
    share_type: int
    status: str
    expire_time: datetime | None
    remark: str | None
    created_time: datetime
    updated_time: datetime
    created_id: int | None
    updated_id: int | None
    # 可包含关联的租户信息
    target_tenant_name: str | None = None


class DataCopySchema(BaseModel):
    """数据复制请求模型"""
    resource_type: str = Field(..., min_length=1, max_length=64, description="资源类型(表名)")
    resource_ids: list[int] = Field(..., min_length=1, description="资源ID列表")
    target_tenant_id: int = Field(..., description="目标租户ID")


class DataCopyResponseSchema(BaseModel):
    """数据复制响应模型"""
    copied_count: int = Field(description="复制数量")
    target_tenant_id: int = Field(description="目标租户ID")
    id_mapping: dict[int, int] = Field(description="ID映射表(旧ID -> 新ID)")


class DataShareListSchema(BaseModel):
    """数据分享列表查询模型"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    resource_type: str | None = Field(None, description="资源类型")
    target_tenant_id: int | None = Field(None, description="目标租户ID")
    share_type: int | None = Field(None, description="分享类型")
    status: str | None = Field(None, description="状态")
