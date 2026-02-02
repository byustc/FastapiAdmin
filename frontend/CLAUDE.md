

## 前端架构

- **状态管理**：Pinia + persistence-plugin 持久化插件
- **路由**：Vue Router 4，配置位于 `frontend/src/router/`
- **API 层**：基于 Axios 的服务，位于 `frontend/src/api/`
- **组件**：可复用组件，位于 `frontend/src/components/`
- **视图**：页面组件，位于 `frontend/src/views/`，按模块组织

添加新的后端插件时，需要相应创建：
1. API 服务文件于 `frontend/src/api/module_*/`
2. 视图组件于 `frontend/src/views/module_*/`
3. 在 `frontend/src/router/index.ts` 中注册路由



## 前端代码质量工具

```bash
# TypeScript 类型检查
pnpm run type-check

# 单独运行各项检查
pnpm run lint:eslint    # ESLint 检查
pnpm run lint:prettier  # Prettier 格式化
pnpm run lint:stylelint # Stylelint 样式检查
```