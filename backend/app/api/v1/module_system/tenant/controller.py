from fastapi import APIRouter, Depends, Path

from fastapi.responses import JSONResponse
from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_system.tenant.schema import (
    TenantCreateSchema,
    TenantListSchema,
    TenantOutSchema,
    TenantUpdateSchema,
)
from app.api.v1.module_system.tenant.service import TenantService
from app.common.response import SuccessResponse

from app.core.dependencies import AuthPermission, db_getter
from app.core.router_class import OperationLogRoute

TenantRouter = APIRouter(route_class=OperationLogRoute, prefix="/tenant", tags=["租户管理"])


@TenantRouter.post("/create", summary="创建租户")
async def create_tenant(
    obj_in: TenantCreateSchema,
    auth: AuthSchema = Depends(
        AuthPermission(["system:tenant:create"], check_data_scope=False)
    ),
) -> JSONResponse:
    """
    创建租户

    权限：system:tenant:create
    """
    result = await TenantService.create_service(obj_in=obj_in, auth=auth)
    return SuccessResponse(data=TenantOutSchema.model_validate(result))


@TenantRouter.put("/update", summary="更新租户")
async def update_tenant(
    obj_in: TenantUpdateSchema,
    auth: AuthSchema = Depends(
        AuthPermission(["system:tenant:update"], check_data_scope=False)
    ),
) -> JSONResponse:
    """
    更新租户

    权限：system:tenant:update
    """
    result = await TenantService.update_service(obj_in=obj_in, auth=auth)
    return SuccessResponse(data=TenantOutSchema.model_validate(result))


@TenantRouter.delete("/delete", summary="删除租户")
async def delete_tenant(
    ids: list[int],
    auth: AuthSchema = Depends(
        AuthPermission(["system:tenant:delete"], check_data_scope=False)
    ),
) -> JSONResponse:
    """
    删除租户（软删除）

    权限：system:tenant:delete

    注意：如果租户存在关联数据（用户/部门/角色），则无法删除
    """
    delete_count = await TenantService.delete_service(ids=ids, auth=auth)
    return SuccessResponse(msg=f"成功删除 {delete_count} 个租户")


@TenantRouter.get("/detail/{id}", summary="获取租户详情")
async def get_tenant_detail(
    id: int = Path(..., description="租户ID"),
    auth: AuthSchema = Depends(
        AuthPermission(["system:tenant:query"], check_data_scope=False)
    ),
) -> JSONResponse:
    """
    获取租户详情

    权限：system:tenant:query
    """
    result = await TenantService.detail_service(tenant_id=id, auth=auth)
    return SuccessResponse(data=TenantOutSchema.model_validate(result))


@TenantRouter.get("/list", summary="获取租户列表")
async def get_tenant_list(
    obj_in: TenantListSchema = Depends(),
    auth: AuthSchema = Depends(
        AuthPermission(["system:tenant:query"], check_data_scope=False)
    ),
) -> JSONResponse:
    """
    获取租户列表（分页）

    权限：system:tenant:query
    """
    result = await TenantService.list_service(obj_in=obj_in, auth=auth)
    return SuccessResponse(data=result)


@TenantRouter.get("/all", summary="获取所有租户")
async def get_all_tenants(
    auth: AuthSchema = Depends(
        AuthPermission(["system:tenant:query"], check_data_scope=False)
    ),
) -> JSONResponse:
    """
    获取所有租户（不分页，用于下拉选择）

    权限：system:tenant:query

    默认只返回启用的租户
    """
    result = await TenantService.all_service(auth=auth)
    data = [TenantOutSchema.model_validate(t) for t in result]
    return SuccessResponse(data=data)
