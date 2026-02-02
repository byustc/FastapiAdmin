

## 后端架构

### 插件化自动发现系统

需要理解的最关键的架构模式：**所有后端功能都以插件形式实现**，位于 `backend/app/plugin/`，系统会自动发现并注册路由。

**自动发现机制**（`backend/app/core/discover.py`）：
1. 扫描 `backend/app/plugin/` 下所有以 `module_` 开头的目录
2. 递归查找这些目录下的所有 `controller.py` 文件
3. 提取这些文件中定义的所有 `APIRouter` 实例
4. 自动注册，URL 前缀映射规则：`module_xxx` -> `/xxx`

**无需手动注册路由**。只需在 `module_*` 目录下创建 `controller.py` 即可。

### 插件模块结构

`backend/app/plugin/module_*/` 下的每个插件模块遵循以下标准结构：

```
module_yourfeature/
└── submodule/
    ├── controller.py    # APIRouter 实例 - 自动注册
    ├── model.py         # SQLAlchemy 数据库模型
    ├── schema.py        # Pydantic 数据验证模型
    ├── service.py       # 业务逻辑层
    └── crud.py          # 数据库 CRUD 操作
```
**分层架构**：Controller（控制器）→ Service（业务逻辑）→ CRUD（数据访问）→ Model（数据模型）

### 核心后端目录

- `app/api/v1/` - 核心系统模块（system、monitor、common）- 手动注册
  - `module_system/tenant/` - 租户管理模块
  - `module_system/share/` - 数据分享模块
- `app/plugin/` - 自动发现的插件模块 - 添加新功能的地方
- `app/core/` - 核心功能（认证、依赖、异常处理、日志、权限）
  - `base_model.py` - 基础模型类（ModelMixin、UserMixin、TenantMixin）
  - `permission.py` - 权限过滤系统（支持5级/6级数据权限）
- `app/common/` - 共享工具、枚举、响应模式
- `app/config/` - 使用 Pydantic Settings 的配置管理
- `app/utils/` - 工具函数

### 控制器编写规范

所有控制器必须：
1. 使用 FastAPI 的 `APIRouter`，并设置 `route_class=OperationLogRoute` 以自动记录操作日志
2. 应用 `AuthPermission` 依赖进行 RBAC 权限控制
3. 返回 `app.common.response` 中的 `SuccessResponse` 或 `ErrorResponse`
4. 包含 summary 文档字符串

```python
from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from app.core.router_class import OperationLogRoute
from app.core.dependencies import AuthPermission
from app.api.v1.module_system.auth.schema import AuthSchema
from app.common.response import SuccessResponse
from .service import YourService

YourRouter = APIRouter(
    route_class=OperationLogRoute,
    prefix="/yourfeature",
    tags=["Your Feature"]
)

@YourRouter.get("/detail/{id}", summary="获取详情")
async def get_detail(
    id: int = Path(..., description="ID"),
    auth: AuthSchema = Depends(AuthPermission(["module_yourfeature:submodule:action"]))
) -> JSONResponse:
    result = await YourService.detail_service(id=id, auth=auth)
    return SuccessResponse(data=result)
```

### 开发规范

1. **命名规范**：模块名采用 `module_xxx` 格式，控制器名采用驼峰命名法
2. **权限控制**：所有 API 接口必须添加权限控制装饰器
3. **日志记录**：使用 `OperationLogRoute` 类自动记录操作日志
4. **返回格式**：统一使用 `SuccessResponse` 或 `ErrorResponse` 返回响应
5. **代码注释**：为所有 API 接口添加详细的文档字符串