# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 提供在此代码库中工作的指导。

## 项目概述

FastAPI Admin 是一套现代化全栈快速开发平台，采用 **前后端分离架构**。后端采用基于插件的可自动发现路由系统，前端使用 Vue3 + TypeScript 构建。

**核心架构原则**：后端采用插件化架构，模块自动发现并注册。新功能应作为插件在 `backend/app/plugin/module_*/` 中开发。

## 技术栈

### 后端技术栈
- FastAPI 0.115+ - 现代异步 Web 框架
- SQLAlchemy 2.0 - 强大的 ORM 库
- Pydantic 2.5 - 数据验证和序列化
- Alembic - 数据库迁移
- APScheduler - 定时任务
- PyJWT - JWT 认证
- Redis - 缓存和会话管理
- LangChain - AI/LLM 集成框架
- Uvicorn - ASGI 服务器

### 前端技术栈
- Vue 3.5+ - 渐进式 JavaScript 框架
- TypeScript - 静态类型检查
- Vite 6 - 构建工具和开发服务器
- Element Plus - 企业级 UI 组件库
- Pinia - 状态管理
- Vue Router 4 - 客户端路由
- UnoCSS - 原子化 CSS 框架
- ESLint + Prettier - 代码格式化和检查


## 📦 工程结构概览
```sh
FastapiAdmin
├─ backend               # 后端工程 (FastAPI + Python)
├─ frontend              # Web前端工程 (Vue3 + Element Plus)
├─ devops                # 部署配置
├─ docker-compose.yaml   # Docker编排文件
├─ deploy.sh             # 一键部署脚本
├─ LICENSE               # 开源协议
|─ README.en.md          # 英文文档
└─ README.md             # 中文文档
```


## 开发命令

### 后端 (Python 3.10+, FastAPI)

后端使用通过 `main.py` (基于 Typer) 构建的自定义 CLI。

```bash
cd backend

# 使用传统 pip 方式
pip install -r requirements.txt
python main.py run                # 启动开发服务器
python main.py run --env=dev      # 指定开发环境启动
python main.py run --env=prod     # 指定生产环境启动

# 数据库迁移（Alembic）
python main.py revision --env=dev     # 生成迁移脚本
python main.py upgrade --env=dev      # 应用迁移
```

**启动前注意**：
- 确保已创建 MySQL/PostgreSQL 数据库
- 确保 Redis 服务正在运行
- 确保环境文件已配置（见下方配置文件部分）

### 前端 (Node.js 20+, Vue3)

```bash
cd frontend

pnpm install              # 安装依赖（必须使用 pnpm）
pnpm run dev             # 启动开发服务器
pnpm run build           # 构建生产版本
pnpm run lint            # 运行所有代码检查（ESLint + Prettier + Stylelint）
```

### Docker 部署

```bash
chmod +x deploy.sh
./deploy.sh              # 一键部署
./deploy.sh --logs       # 查看容器日志
./deploy.sh --stop       # 停止服务
```


## 配置文件

### 后端配置
- `backend/env/.env.dev` - 开发环境配置（需从 `.env.dev.example` 重命名）
- `backend/env/.env.prod` - 生产环境配置（需从 `.env.prod.example` 重命名）
- `backend/alembic.ini` - 数据库迁移配置
- `backend/pyproject.toml` - 项目元数据和 uv 依赖管理

### 前端配置
- `frontend/.env.development` - 前端开发环境配置（需从 `.env.development.example` 重命名）
- `frontend/.env.production` - 前端生产环境配置（需从 `.env.production.example` 重命名）
- `frontend/vite.config.ts` - Vite 构建配置


## 多租户架构

系统支持基于租户的多机构/组织数据隔离架构。

### 架构特性

**三层隔离机制**：
1. **租户隔离** - 不同机构/组织间的数据完全隔离
2. **部门隔离** - 租户内部的部门级数据隔离
3. **用户隔离** - 用户个人数据隔离（created_id）

**数据分享机制**：
- 支持跨租户数据分享（只读或可编辑）
- 可设置分享有效期
- 支持按资源类型和资源ID精确控制

### 核心组件

#### 1. TenantMixin（租户混入类）

位于 `backend/app/core/base_model.py`，为需要租户隔离的模型提供 `tenant_id` 字段。

```python
from app.core.base_model import ModelMixin, UserMixin, TenantMixin

# 需要租户隔离的模型
class YourModel(ModelMixin, UserMixin, TenantMixin):
    __tablename__ = "your_table"
    # ... 其他字段

# 不需要租户隔离的模型
class AnotherModel(ModelMixin, UserMixin):
    __tablename__ = "another_table"
    # ... 其他字段
```

#### 2. 权限系统扩展

位于 `backend/app/core/permission.py`，支持 **6级数据权限**（启用租户隔离时）：

| data_scope | 值 | 描述 |
|------------|---|------|
| DATA_SCOPE_SELF | 1 | 仅本人数据 |
| DATA_SCOPE_DEPT | 2 | 本部门数据 |
| DATA_SCOPE_DEPT_AND_CHILD | 3 | 本部门及以下数据 |
| DATA_SCOPE_TENANT | 4 | 本租户数据（新增） |
| DATA_SCOPE_ALL | 5 | 全部数据 |
| DATA_SCOPE_CUSTOM | 6 | 自定义数据 |

#### 3. 租户管理模块

位于 `backend/app/api/v1/module_system/tenant/`，提供租户的完整 CRUD 功能：
- 租户创建、更新、删除、查询
- 租户状态管理（启用/禁用）
- 租户配额管理

#### 4. 数据分享模块

位于 `backend/app/api/v1/module_system/share/`，实现跨租户数据分享：
- 支持两种分享类型：
  - `share_type=1` - 仅查看
  - `share_type=2` - 查看和编辑
- 支持设置分享有效期（expire_time）
- 支持分享状态控制（status: 0=生效, 1=失效）
- 删除操作不支持分享数据（安全机制）

### 模型更新

以下核心模型已添加租户关联：
- `UserModel` - 用户关联租户
- `RoleModel` - 角色关联租户
- `DeptModel` - 部门关联租户

### 权限过滤逻辑

权限过滤系统（6级权限，含租户隔离）：

```python
from app.core.permission import Permission

# 创建权限过滤器
permission = Permission(
    model=YourModel,
    auth=auth,
    operation_type="read"  # 可选: "read", "update", "delete"
)

# 应用权限过滤
query = select(YourModel)
filtered_query = await permission.filter_query(query)
```

**权限过滤优先级**（OR 逻辑）：
1. 本租户数据（tenant_id 匹配）
2. 分享的数据（跨租户访问通道）
3. 部门权限（原有逻辑）

**操作类型限制**：
- `read` - 包含 share_type=1 和 share_type=2
- `update` - 仅包含 share_type=2
- `delete` - 不包含分享数据

### 数据迁移说明

启用多租户架构时需要注意：
1. 现有数据需要关联到默认租户
2. 用户、角色、部门需要设置 tenant_id
3. 建议在测试环境充分验证后再应用到生产环境

## 开发流程

1. **需求分析**：明确功能需求和业务逻辑
2. **数据库设计**：设计数据库表结构
3. **代码生成**：使用代码生成器生成基础代码
4. **业务逻辑开发**：完善业务逻辑和接口
5. **前端开发**：开发前端页面和交互
6. **测试**：进行单元测试和集成测试
7. **部署**：部署到生产环境

## 测试规范

后端使用 pytest（配置于 `backend/tests/`）：
```bash
cd backend
pytest                        # 运行所有测试
pytest tests/test_specific.py # 运行特定测试文件
```


## 重要注意事项

1. **环境配置**：首次运行前务必将 `.env.*.example` 文件复制为 `.env.*` 并根据实际情况修改配置
2. **数据库迁移**：模型变更后务必生成并应用迁移
3. **权限格式**：使用 `module:submodule:action` 格式的 RBAC 权限（如 `module_application:ai:chat`）
4. **异步编程**：所有数据库操作和 service 方法都是异步的，必须使用 await
5. **插件命名**：模块目录必须以 `module_` 前缀开头才能被自动发现
6. **速率限制**：所有路由都通过 FastAPILimiter 应用速率限制（基于 Redis）
7. **权限控制**：所有 API 接口必须添加权限控制装饰器
8. **数据验证**：所有输入数据必须进行验证
9. **异常处理**：统一处理 API 异常
10. **日志记录**：关键操作必须记录日志
11. **性能优化**：注意 API 性能优化，避免慢查询
12. **代码规范**：遵循 PEP8 和项目代码规范
13. **租户隔离**：开发需要租户隔离的模型时，继承 `TenantMixin`；不需要时则不继承
14. **权限系统**：使用6级权限系统（含租户隔离），data_scope: 1-本人 2-本部门 3-部门及以下 4-本租户 5-全部 6-自定义

## 常见问题

**Q：如何添加新功能模块？**
A：在 `backend/app/plugin/` 目录下创建新的模块目录（如 `module_yourfeature`），编写 controller、model、schema、service、crud 文件即可。系统会自动发现并注册路由。

**Q：如何配置数据库？**
A：在 `backend/env/.env.dev` 或 `backend/env/.env.prod` 文件中配置数据库连接信息。

**Q：如何配置 Redis？**
A：在 `backend/env/.env.dev` 或 `backend/env/.env.prod` 文件中配置 Redis 连接信息。

**Q：如何生成数据库迁移文件？**
A：使用 `python main.py revision --env=dev` 命令生成迁移文件。

**Q：如何应用数据库迁移？**
A：使用 `python main.py upgrade --env=dev` 命令应用迁移。

**Q：如何启动开发服务器？**
A：后端使用 `python main.py run --env=dev`，前端使用 `pnpm run dev`。

**Q：如何构建前端生产版本？**
A：使用 `pnpm run build` 命令构建前端生产版本。

**Q：如何部署到生产环境？**
A：使用 `./deploy.sh` 脚本一键部署到生产环境。

**Q：如何创建需要租户隔离的模型？**
A：让模型同时继承 `ModelMixin`、`UserMixin` 和 `TenantMixin`：
```python
from app.core.base_model import ModelMixin, UserMixin, TenantMixin

class YourModel(ModelMixin, UserMixin, TenantMixin):
    __tablename__ = "your_table"
```

**Q：租户隔离和权限系统如何工作？**
A：系统默认使用6级权限系统（含租户隔离）：
1-本人 2-本部门 3-部门及以下 4-本租户 5-全部 6-自定义

**Q：如何实现跨租户数据分享？**
A：通过数据分享模块（`backend/app/api/v1/module_system/share/`）创建分享记录：
- 设置目标租户ID（target_tenant_id）
- 设置资源类型（resource_type，表名）
- 设置资源ID（resource_id）
- 设置分享类型（share_type: 1=仅查看, 2=查看和编辑）
- 可选设置过期时间（expire_time）

**Q：分享的数据可以删除吗？**
A：不可以。删除操作不包含分享数据，这是安全机制设计，防止误删跨租户分享的数据。


