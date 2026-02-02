"""add tenant support

Revision ID: 001
Revises:
Create Date: 2025-02-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ========== 创建租户表 ==========
    op.create_table(
        'sys_tenant',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('code', sa.String(length=32), nullable=False),
        sa.Column('short_name', sa.String(length=64), nullable=True),
        sa.Column('logo', sa.String(length=500), nullable=True),
        sa.Column('tenant_type', sa.Integer(), nullable=True),
        sa.Column('contact_person', sa.String(length=64), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('contact_email', sa.String(length=128), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=10), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.Column('updated_time', sa.DateTime(), nullable=False),
        sa.Column('created_id', sa.Integer(), nullable=True),
        sa.Column('updated_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.UniqueConstraint('code'),
        comment='租户表'
    )
    op.create_index('ix_sys_tenant_code', 'sys_tenant', ['code'])

    # ========== 创建数据分享表 ==========
    op.create_table(
        'sys_data_share',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('uuid', sa.String(length=64), nullable=False),
        sa.Column('resource_type', sa.String(length=64), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.Column('target_tenant_id', sa.Integer(), nullable=False),
        sa.Column('share_type', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=10), nullable=False, server_default='0'),
        sa.Column('expire_time', sa.DateTime(), nullable=True),
        sa.Column('remark', sa.Text(), nullable=True),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.Column('updated_time', sa.DateTime(), nullable=False),
        sa.Column('created_id', sa.Integer(), nullable=True),
        sa.Column('updated_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uuid'),
        sa.ForeignKeyConstraint(['target_tenant_id'], ['sys_tenant.id'],
                               ondelete='CASCADE', onupdate='CASCADE'),
        comment='数据分享表'
    )
    op.create_index('ix_sys_data_share_resource', 'sys_data_share',
                    ['resource_type', 'resource_id'])
    op.create_index('ix_sys_data_share_target_tenant', 'sys_data_share',
                    ['target_tenant_id'])

    # ========== 修改用户表 ==========
    op.add_column('sys_user',
                  sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.create_index('ix_sys_user_tenant_id', 'sys_user', ['tenant_id'])
    op.create_foreign_key('fk_sys_user_tenant_id', 'sys_user', 'sys_tenant',
                         ['tenant_id'], ['id'], ondelete='SET NULL')

    # ========== 修改部门表 ==========
    op.add_column('sys_dept',
                  sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.create_index('ix_sys_dept_tenant_id', 'sys_dept', ['tenant_id'])
    op.create_foreign_key('fk_sys_dept_tenant_id', 'sys_dept', 'sys_tenant',
                         ['tenant_id'], ['id'], ondelete='SET NULL')

    # ========== 修改角色表 ==========
    op.add_column('sys_role',
                  sa.Column('tenant_id', sa.Integer(), nullable=True))
    op.create_index('ix_sys_role_tenant_id', 'sys_role', ['tenant_id'])
    op.create_foreign_key('fk_sys_role_tenant_id', 'sys_role', 'sys_tenant',
                         ['tenant_id'], ['id'], ondelete='SET NULL')


def downgrade():
    # 回滚操作
    op.drop_constraint('fk_sys_role_tenant_id', 'sys_role')
    op.drop_index('ix_sys_role_tenant_id', 'sys_role')
    op.drop_column('sys_role', 'tenant_id')

    op.drop_constraint('fk_sys_dept_tenant_id', 'sys_dept')
    op.drop_index('ix_sys_dept_tenant_id', 'sys_dept')
    op.drop_column('sys_dept', 'tenant_id')

    op.drop_constraint('fk_sys_user_tenant_id', 'sys_user')
    op.drop_index('ix_sys_user_tenant_id', 'sys_user')
    op.drop_column('sys_user', 'tenant_id')

    op.drop_table('sys_data_share')
    op.drop_table('sys_tenant')
