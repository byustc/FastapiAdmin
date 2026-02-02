from fastapi import APIRouter, Depends, Path

from fastapi.responses import JSONResponse
from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_system.share.schema import (
    DataCopyResponseSchema,
    DataCopySchema,
    DataShareCreateSchema,
    DataShareListSchema,
    DataShareOutSchema,
)
from app.api.v1.module_system.share.service import ShareService
from app.common.response import SuccessResponse

from app.core.dependencies import AuthPermission
from app.core.router_class import OperationLogRoute

ShareRouter = APIRouter(route_class=OperationLogRoute, prefix="/share", tags=["数据分享"])


@ShareRouter.post("/create", summary="创建数据分享")
async def create_share(
    obj_in: DataShareCreateSchema,
    auth: AuthSchema = Depends(AuthPermission(["system:share:create"], check_data_scope=False)),
) -> JSONResponse:
    """
    创建数据分享

    权限：system:share:create

    分享无需审批，创建后立即生效
    """
    result = await ShareService.create_share_service(obj_in=obj_in, auth=auth)
    return SuccessResponse(data=DataShareOutSchema.model_validate(result))


@ShareRouter.get("/list", summary="获取分享列表")
async def get_share_list(
    obj_in: DataShareListSchema = Depends(),
    auth: AuthSchema = Depends(AuthPermission(["system:share:query"], check_data_scope=False)),
) -> JSONResponse:
    """
    获取分享列表（分页）

    权限：system:share:query
    """
    result = await ShareService.list_service(obj_in=obj_in, auth=auth)
    return SuccessResponse(data=result)


@ShareRouter.delete("/revoke/{share_id}", summary="撤销数据分享")
async def revoke_share(
    share_id: int = Path(..., description="分享ID"),
    auth: AuthSchema = Depends(AuthPermission(["system:share:revoke"], check_data_scope=False)),
) -> JSONResponse:
    """
    撤销数据分享（软删除）

    权限：system:share:revoke
    """
    await ShareService.revoke_share_service(share_id=share_id, auth=auth)
    return SuccessResponse(msg="分享已撤销")


@ShareRouter.post("/copy", summary="复制数据到目标租户")
async def copy_data(
    obj_in: DataCopySchema,
    auth: AuthSchema = Depends(AuthPermission(["system:share:copy"], check_data_scope=False)),
) -> JSONResponse:
    """
    复制数据到目标租户

    权限：system:share:copy

    说明：
    - 仅复制主表数据，不复制关联数据
    - 复制后的数据完全独立，与源数据无关联
    - 返回新旧ID映射关系
    """
    result = await ShareService.copy_data_service(obj_in=obj_in, auth=auth)
    return SuccessResponse(data=DataCopyResponseSchema.model_validate(result))
