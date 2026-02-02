from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TenantBaseSchema(BaseModel):
    """租户基础模型"""
    name: str = Field(..., min_length=1, max_length=128, description="租户名称")
    code: str = Field(..., min_length=1, max_length=32, description="租户编码")
    short_name: str | None = Field(None, max_length=64, description="租户简称")
    logo: str | None = Field(None, max_length=500, description="租户Logo URL")
    tenant_type: int | None = Field(None, ge=0, le=4, description="租户类型(0:企业 1:政府 2:学校 3:医院 4:其他)")
    contact_person: str | None = Field(None, max_length=64, description="联系人")
    contact_phone: str | None = Field(None, max_length=20, description="联系电话")
    contact_email: str | None = Field(None, max_length=128, description="联系邮箱")
    address: str | None = Field(None, max_length=500, description="地址")
    description: str | None = Field(None, description="备注")
    is_active: bool = Field(True, description="是否启用")


class TenantCreateSchema(TenantBaseSchema):
    """租户创建模型"""
    pass


class TenantUpdateSchema(BaseModel):
    """租户更新模型"""
    id: int = Field(..., description="租户ID")
    name: str | None = Field(None, min_length=1, max_length=128, description="租户名称")
    short_name: str | None = Field(None, max_length=64, description="租户简称")
    logo: str | None = Field(None, max_length=500, description="租户Logo URL")
    tenant_type: int | None = Field(None, ge=0, le=4, description="租户类型")
    contact_person: str | None = Field(None, max_length=64, description="联系人")
    contact_phone: str | None = Field(None, max_length=20, description="联系电话")
    contact_email: str | None = Field(None, max_length=128, description="联系邮箱")
    address: str | None = Field(None, max_length=500, description="地址")
    description: str | None = Field(None, description="备注")
    is_active: bool | None = Field(None, description="是否启用")


class TenantOutSchema(BaseModel):
    """租户输出模型"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: str
    name: str
    code: str
    short_name: str | None
    logo: str | None
    tenant_type: int | None
    contact_person: str | None
    contact_phone: str | None
    contact_email: str | None
    address: str | None
    is_active: bool
    status: str
    description: str | None
    created_time: datetime
    updated_time: datetime
    created_id: int | None
    updated_id: int | None


class TenantListSchema(BaseModel):
    """租户列表查询模型"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    name: str | None = Field(None, description="租户名称（模糊查询）")
    code: str | None = Field(None, description="租户编码（模糊查询）")
    tenant_type: int | None = Field(None, description="租户类型")
    is_active: bool | None = Field(None, description="是否启用")
    status: str | None = Field(None, description="状态")
