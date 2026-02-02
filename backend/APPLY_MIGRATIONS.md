# Database Migration Guide

## Prerequisites

1. **MySQL Database Setup**
   - Ensure MySQL is running on localhost:3306
   - Create the database:
   ```sql
   CREATE DATABASE fastapiadmin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
   - Ensure your root password matches what's in `.env.dev`

2. **Environment Configuration**
   - File: `backend/env/.env.dev`
   - Current settings:
     ```
     DATABASE_HOST = "localhost"
     DATABASE_PORT = 3306
     DATABASE_USER = "root"
     DATABASE_PASSWORD = "root"  # Update if needed
     DATABASE_NAME = "fastapiadmin"
     ```

3. **Dependencies Installed**
   - All required Python packages must be installed
   - Run: `pip install -r requirements.txt` (Python 3.11 recommended)

## Applying Migrations

### Option 1: Using Python Directly (Recommended)

```bash
cd backend

# Check current migration state
python -c "import sys; print('Python:', sys.version); import aiomysql; print('aiomysql: OK')"

# Set environment variable and run alembic
set ENVIRONMENT=dev
python -m alembic current
python -m alembic upgrade head
```

### Option 2: Using main.py

```bash
cd backend

# If you have the main.py CLI working
python main.py upgrade --env=dev
```

### Option 3: Using alembic directly

```bash
cd backend

# Create a simple batch file to set environment
# Create file: run_alembic.bat
@echo off
set ENVIRONMENT=dev
python -m alembic %*
```

Then run:
```bash
run_alembic.bat current
run_alembic.bat upgrade head
```

## What the Migration Does

The `001_add_tenant_support.py` migration will:

1. **Create `sys_tenant` table** - Stores tenant information
2. **Create `sys_data_share` table** - Manages cross-tenant data sharing
3. **Add `tenant_id` column** to:
   - `sys_user` table
   - `sys_role` table
   - `sys_dept` table
4. **Create indexes and foreign keys** for proper data integrity

## Post-Migration Steps

After successfully applying the migration:

1. **Create default tenant** (ID=1):
   ```sql
   INSERT INTO sys_tenant (uuid, name, code, short_name, tenant_type, is_active, status, created_time, updated_time)
   VALUES ('default-tenant-uuid', 'Default Tenant', 'default', 'Default', 0, 1, '0', NOW(), NOW());
   ```

2. **Migrate existing data** - Update existing users/roles/depts to belong to the default tenant:
   ```sql
   UPDATE sys_user SET tenant_id = 1 WHERE tenant_id IS NULL;
   UPDATE sys_role SET tenant_id = 1 WHERE tenant_id IS NULL;
   UPDATE sys_dept SET tenant_id = 1 WHERE tenant_id IS NULL;
   ```

3. **Verify the migration**:
   ```bash
   python -m alembic current
   # Should show: 001
   ```

## Troubleshooting

### Error: "Access denied for user 'root'"
**Solution**: Update DATABASE_PASSWORD in `backend/env/.env.dev` to match your actual MySQL password.

### Error: "ModuleNotFoundError: No module named 'aiomysql'"
**Solution**: Install dependencies:
```bash
pip install aiomysql pymysql
```

### Error: "Database doesn't exist"
**Solution**: Create the database first:
```sql
CREATE DATABASE fastapiadmin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Error: "Target database is not up to date"
**Solution**: This means there are pending migrations. Run:
```bash
python -m alembic upgrade head
```

## Verification

To verify the migration was successful:

```bash
# Check migration version
python -m alembic current

# Check database tables
mysql -u root -p fastapiadmin -e "SHOW TABLES LIKE 'sys_%';"

# Check new columns
mysql -u root -p fastapiadmin -e "DESCRIBE sys_user;" | grep tenant_id
mysql -u root -p fastapiadmin -e "DESCRIBE sys_role;" | grep tenant_id
mysql -u root -p fastapiadmin -e "DESCRIBE sys_dept;" | grep tenant_id
```
