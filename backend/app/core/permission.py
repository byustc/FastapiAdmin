from datetime import datetime
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.sql.elements import ColumnElement

from app.api.v1.module_system.auth.schema import AuthSchema
from app.api.v1.module_system.dept.model import DeptModel
from app.api.v1.module_system.user.model import UserModel
from app.config.setting import settings
from app.utils.common_util import get_child_id_map, get_child_recursion


class Permission:
    """
    为业务模型提供数据权限过滤功能

    支持多租户架构，使用6级数据权限（含租户隔离）：
    data_scope: 1-仅本人 2-本部门 3-本部门及以下 4-本租户 5-全部 6-自定义
    """

    # 数据权限常量定义，提高代码可读性
    DATA_SCOPE_SELF = 1  # 仅本人数据
    DATA_SCOPE_DEPT = 2  # 本部门数据
    DATA_SCOPE_DEPT_AND_CHILD = 3  # 本部门及以下数据
    DATA_SCOPE_TENANT = 4  # 本租户数据
    DATA_SCOPE_ALL = 5  # 全部数据
    DATA_SCOPE_CUSTOM = 6  # 自定义数据

    def __init__(self, model: Any, auth: AuthSchema, operation_type: str = "read") -> None:
        """
        初始化权限过滤器实例

        Args:
            model: 数据模型类
            auth: 认证信息对象
            operation_type: 操作类型 ("read", "update", "delete")，用于分享权限控制
        """
        self.model = model
        self.auth = auth
        self.operation_type = operation_type
        self.conditions: list[ColumnElement] = []  # 权限条件列表

    async def filter_query(self, query: Any) -> Any:
        """
        异步过滤查询对象

        Args:
            query: SQLAlchemy查询对象

        Returns:
            过滤后的查询对象
        """
        condition = await self._permission_condition()
        return query.where(condition) if condition is not None else query

    async def _permission_condition(self) -> ColumnElement | None:
        """
        应用数据范围权限隔离（入口方法）

        使用新的6级权限系统（含租户隔离）：
        data_scope: 1-仅本人 2-本部门 3-本部门及以下 4-本租户 5-全部 6-自定义
        """
        return await self._new_permission_condition()

    async def _new_permission_condition(self) -> ColumnElement | None:
        """
        新的权限过滤逻辑（支持租户隔离）

        三层权限过滤：租户 > 部门 > 用户

        data_scope: 1-仅本人 2-本部门 3-本部门及以下 4-本租户 5-全部 6-自定义

        权限逻辑：
        1. 租户隔离：用户只能访问本租户数据（data_scope=4）或全部数据（data_scope=5）
        2. 数据分享：跨租户数据可通过分享表访问
        3. 部门隔离：原有的部门权限逻辑保持不变
        4. 用户隔离：created_id 隔离保持不变
        """
        # 0. 前置检查
        if not self.auth.user or not self.auth.check_data_scope:
            return None

        if self.auth.user.is_superuser:
            return None

        # 1. 检查模型是否有租户字段和创建者字段
        has_tenant_field = hasattr(self.model, "tenant_id")
        has_created_id_field = hasattr(self.model, "created_id")

        if not has_tenant_field and not has_created_id_field:
            # 既没有租户字段也没有创建者字段，不需要权限过滤
            return None

        # 2. 获取用户可访问的租户ID列表
        accessible_tenant_ids = await self._get_accessible_tenants()

        # 3. 获取分享给用户租户的资源ID列表
        shared_resource_ids = await self._get_shared_resources()

        # 4. 获取部门权限条件（原有逻辑）
        dept_condition = await self._get_dept_permission_condition()

        # 5. 构建最终查询条件
        conditions = []

        # 条件A: 本租户数据
        if has_tenant_field and accessible_tenant_ids:
            conditions.append(
                self.model.tenant_id.in_(list(accessible_tenant_ids))
            )

        # 条件B: 分享的数据（跨租户访问通道）
        if shared_resource_ids:
            conditions.append(
                self.model.id.in_(list(shared_resource_ids))
            )

        # 条件C: 部门权限（原有逻辑，适配新的 data_scope 值）
        if dept_condition is not None:
            conditions.append(dept_condition)

        # 组合条件：满足任一条件即可访问 (OR 逻辑)
        if conditions:
            return or_(*conditions)

        # 默认：无权限
        return self.model.id == -1

    async def _get_accessible_tenants(self) -> set[int]:
        """
        获取用户可访问的租户ID列表

        基于角色的 data_scope 设置：
        - DATA_SCOPE_ALL (5): 返回所有租户ID
        - DATA_SCOPE_TENANT (4): 返回用户所在租户ID
        - 其他 (1/2/3/6): 默认返回用户所在租户ID
        """
        tenant_ids = set()

        # 获取用户所在租户
        user_tenant_id = getattr(self.auth.user, "tenant_id", None)

        if not user_tenant_id:
            # 用户没有关联租户，返回空集合（无权限）
            return tenant_ids

        # 获取用户的所有角色
        roles = getattr(self.auth.user, "roles", []) or []
        if not roles:
            # 用户没有角色，默认只能访问本租户
            return {user_tenant_id}

        # 收集所有角色的 data_scope
        data_scopes = set()
        for role in roles:
            data_scopes.add(role.data_scope)

        # 优先级处理
        if self.DATA_SCOPE_ALL in data_scopes:
            # 全部数据权限：返回所有租户ID
            from app.api.v1.module_system.tenant.model import TenantModel

            sql = select(TenantModel.id).where(TenantModel.is_active == True)
            result = await self.auth.db.execute(sql)
            return set(result.scalars().all())

        # 本租户数据权限或其他权限
        # 默认返回用户所在租户
        tenant_ids.add(user_tenant_id)

        return tenant_ids

    async def _get_shared_resources(self) -> set[int]:
        """
        获取分享给用户租户的资源ID列表

        返回分享给用户租户、且在有效期内、且状态为生效的资源ID
        根据 operation_type 和 share_type 过滤：
        - read: 包含 share_type=1 和 share_type=2
        - update: 仅包含 share_type=2
        - delete: 不包含分享数据（分享的数据不能删除）
        """
        from app.api.v1.module_system.share.model import DataShareModel

        user_tenant_id = getattr(self.auth.user, "tenant_id", None)
        if not user_tenant_id:
            return set()

        # 删除操作不包含分享数据
        if self.operation_type == "delete":
            return set()

        # 根据操作类型确定允许的分享类型
        if self.operation_type == "read":
            allowed_share_types = [1, 2]  # 仅查看 + 查看和编辑
        elif self.operation_type == "update":
            allowed_share_types = [2]  # 仅查看和编辑
        else:
            return set()

        # 查询分享记录
        now = datetime.now()
        sql = select(DataShareModel.resource_id).where(
            and_(
                DataShareModel.target_tenant_id == user_tenant_id,
                DataShareModel.resource_type == self.model.__tablename__,
                DataShareModel.status == "0",  # 生效状态
                DataShareModel.share_type.in_(allowed_share_types),
                (
                    (DataShareModel.expire_time.is_(None))
                    | (DataShareModel.expire_time > now)
                ),
            )
        )

        result = await self.auth.db.execute(sql)
        return set(result.scalars().all())

    async def _get_dept_permission_condition(self) -> ColumnElement | None:
        """
        获取部门权限条件（适配新的 data_scope 值）

        data_scope: 1-仅本人 2-本部门 3-本部门及以下 4-本租户 5-全部 6-自定义

        注意：data_scope=4（本租户）已在 _get_accessible_tenants 中处理
        """
        # 如果模型没有创建者字段，不应用部门权限
        if not hasattr(self.model, "created_id"):
            return None

        # 如果用户没有角色，只能查看自己的数据
        roles = getattr(self.auth.user, "roles", []) or []
        if not roles:
            created_id_attr = getattr(self.model, "created_id", None)
            if created_id_attr is not None:
                return created_id_attr == self.auth.user.id
            return None

        # 获取用户所有角色的权限范围
        data_scopes = set()
        custom_dept_ids = set()

        for role in roles:
            data_scopes.add(role.data_scope)
            # 收集自定义权限（data_scope=6）关联的部门ID
            if role.data_scope == self.DATA_SCOPE_CUSTOM and hasattr(role, "depts") and role.depts:
                custom_dept_ids.update(dept.id for dept in role.depts)

        # 权限优先级处理：全部数据权限最高优先级
        if self.DATA_SCOPE_ALL in data_scopes:
            return None

        # 本租户数据权限不在此处理
        if self.DATA_SCOPE_TENANT in data_scopes:
            return None

        # 收集所有可访问的部门ID（2、3、6权限的并集）
        accessible_dept_ids = set()
        user_dept_id = getattr(self.auth.user, "dept_id", None)

        # 处理自定义数据权限（6）
        if self.DATA_SCOPE_CUSTOM in data_scopes:
            accessible_dept_ids.update(custom_dept_ids)

        # 处理本部门数据权限（2）
        if self.DATA_SCOPE_DEPT in data_scopes and user_dept_id is not None:
            accessible_dept_ids.add(user_dept_id)

        # 处理本部门及以下数据权限（3）
        if self.DATA_SCOPE_DEPT_AND_CHILD in data_scopes and user_dept_id is not None:
            try:
                # 查询所有部门并递归获取子部门
                dept_sql = select(DeptModel)
                dept_result = await self.auth.db.execute(dept_sql)
                dept_objs = dept_result.scalars().all()
                id_map = get_child_id_map(dept_objs)
                dept_with_children_ids = get_child_recursion(id=user_dept_id, id_map=id_map)
                accessible_dept_ids.update(dept_with_children_ids)
            except Exception:
                # 查询失败时降级到本部门
                accessible_dept_ids.add(user_dept_id)

        # 如果有部门权限（2、3、6任一），使用部门过滤
        if accessible_dept_ids:
            creator_rel = getattr(self.model, "created_by", None)
            # 优先使用关系过滤（性能更好）
            if creator_rel is not None and hasattr(UserModel, "dept_id"):
                return creator_rel.has(UserModel.dept_id.in_(list(accessible_dept_ids)))
            # 降级方案：如果模型没有created_by关系但有created_id，则只能查看自己的数据
            created_id_attr = getattr(self.model, "created_id", None)
            if created_id_attr is not None:
                return created_id_attr == self.auth.user.id
            return None

        # 处理仅本人数据权限（1）
        if self.DATA_SCOPE_SELF in data_scopes:
            created_id_attr = getattr(self.model, "created_id", None)
            if created_id_attr is not None:
                return created_id_attr == self.auth.user.id
            return None

        # 默认情况：如果用户有角色但没有任何有效权限范围，只能查看自己的数据
        created_id_attr = getattr(self.model, "created_id", None)
        if created_id_attr is not None:
            return created_id_attr == self.auth.user.id
        return None
