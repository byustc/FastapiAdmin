<!-- 租户管理 -->
<template>
  <div class="app-container">
    <!-- 搜索区域 -->
    <div class="search-container">
      <el-form
        ref="queryFormRef"
        :model="queryFormData"
        :inline="true"
        label-suffix=":"
        @submit.prevent="handleQuery"
      >
        <el-form-item prop="name" label="租户名称">
          <el-input v-model="queryFormData.name" placeholder="请输入租户名称" clearable />
        </el-form-item>
        <el-form-item prop="code" label="租户编码">
          <el-input v-model="queryFormData.code" placeholder="请输入租户编码" clearable />
        </el-form-item>
        <el-form-item prop="tenant_type" label="租户类型">
          <el-select
            v-model="queryFormData.tenant_type"
            placeholder="请选择租户类型"
            style="width: 167.5px"
            clearable
          >
            <el-option :value="0" label="企业" />
            <el-option :value="1" label="政府" />
            <el-option :value="2" label="学校" />
            <el-option :value="3" label="医院" />
            <el-option :value="4" label="其他" />
          </el-select>
        </el-form-item>
        <el-form-item prop="is_active" label="状态">
          <el-select
            v-model="queryFormData.is_active"
            placeholder="请选择状态"
            style="width: 167.5px"
            clearable
          >
            <el-option :value="true" label="启用" />
            <el-option :value="false" label="停用" />
          </el-select>
        </el-form-item>
        <!-- 查询、重置按钮 -->
        <el-form-item class="search-buttons">
          <el-button
            v-hasPerm="['system:tenant:query']"
            type="primary"
            icon="search"
            native-type="submit"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['system:tenant:query']"
            icon="refresh"
            @click="handleResetQuery"
          >
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 内容区域 -->
    <el-card class="data-table">
      <template #header>
        <div class="card-header">
          <span>
            <el-tooltip content="租户管理维护系统的租户信息。">
              <QuestionFilled class="w-4 h-4 mx-1" />
            </el-tooltip>
            租户管理列表
          </span>
        </div>
      </template>

      <!-- 功能区域 -->
      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['system:tenant:create']"
                type="success"
                icon="plus"
                @click="handleOpenDialog('create')"
              >
                新增
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['system:tenant:delete']"
                type="danger"
                icon="delete"
                :disabled="selectIds.length === 0"
                @click="handleDelete(selectIds)"
              >
                批量删除
              </el-button>
            </el-col>
          </el-row>
        </div>
        <div class="data-table__toolbar--right">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-tooltip content="刷新">
                <el-button
                  v-hasPerm="['system:tenant:query']"
                  type="primary"
                  icon="refresh"
                  circle
                  @click="handleRefresh"
                />
              </el-tooltip>
            </el-col>
            <el-col :span="1.5">
              <el-popover placement="bottom" trigger="click">
                <template #reference>
                  <el-button type="danger" icon="operation" circle></el-button>
                </template>
                <el-scrollbar max-height="350px">
                  <template v-for="column in tableColumns" :key="column.prop">
                    <el-checkbox v-if="column.prop" v-model="column.show" :label="column.label" />
                  </template>
                </el-scrollbar>
              </el-popover>
            </el-col>
          </el-row>
        </div>
      </div>

      <el-table
        ref="dataTableRef"
        v-loading="loading"
        :data="pageTableData"
        highlight-current-row
        class="data-table__content"
        height="450"
        max-height="450"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <template #empty>
          <el-empty :image-size="80" description="暂无数据" />
        </template>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'selection')?.show"
          type="selection"
          width="55"
          align="center"
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'index')?.show"
          type="index"
          fixed
          label="序号"
          width="60"
        >
          <template #default="scope">
            {{ (queryFormData.page_no - 1) * queryFormData.page_size + scope.$index + 1 }}
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'name')?.show"
          key="name"
          label="租户名称"
          prop="name"
          min-width="150"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'code')?.show"
          key="code"
          label="租户编码"
          prop="code"
          min-width="120"
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'short_name')?.show"
          key="short_name"
          label="租户简称"
          prop="short_name"
          min-width="120"
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'tenant_type')?.show"
          key="tenant_type"
          label="租户类型"
          prop="tenant_type"
          min-width="100"
        >
          <template #default="scope">
            <el-tag v-if="scope.row.tenant_type === 0" type="primary">企业</el-tag>
            <el-tag v-else-if="scope.row.tenant_type === 1" type="success">政府</el-tag>
            <el-tag v-else-if="scope.row.tenant_type === 2" type="warning">学校</el-tag>
            <el-tag v-else-if="scope.row.tenant_type === 3" type="info">医院</el-tag>
            <el-tag v-else-if="scope.row.tenant_type === 4" type="">其他</el-tag>
            <el-tag v-else type="danger">未知</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'contact_person')?.show"
          key="contact_person"
          label="联系人"
          prop="contact_person"
          min-width="100"
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'contact_phone')?.show"
          key="contact_phone"
          label="联系电话"
          prop="contact_phone"
          min-width="130"
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'is_active')?.show"
          key="is_active"
          label="状态"
          prop="is_active"
          min-width="80"
        >
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? "启用" : "停用" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'created_time')?.show"
          key="created_time"
          label="创建时间"
          prop="created_time"
          min-width="200"
          sortable
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'operation')?.show"
          fixed="right"
          label="操作"
          align="center"
          min-width="200"
        >
          <template #default="scope">
            <el-button
              v-hasPerm="['system:tenant:query']"
              type="info"
              size="small"
              link
              icon="document"
              @click="handleOpenDialog('detail', scope.row.id)"
            >
              详情
            </el-button>
            <el-button
              v-hasPerm="['system:tenant:update']"
              type="primary"
              size="small"
              link
              icon="edit"
              @click="handleOpenDialog('update', scope.row.id)"
            >
              编辑
            </el-button>
            <el-button
              v-hasPerm="['system:tenant:delete']"
              type="danger"
              size="small"
              link
              icon="delete"
              @click="handleDelete([scope.row.id])"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页区域 -->
      <template #footer>
        <pagination
          v-model:total="total"
          v-model:page="queryFormData.page_no"
          v-model:limit="queryFormData.page_size"
          @pagination="loadingData"
        />
      </template>
    </el-card>

    <!-- 租户表单弹窗 -->
    <el-dialog
      v-model="dialogVisible.visible"
      :title="dialogVisible.title"
      width="800px"
      @close="handleCloseDialog"
    >
      <!-- 详情 -->
      <template v-if="dialogVisible.type === 'detail'">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="租户名称">
            {{ detailFormData.name }}
          </el-descriptions-item>
          <el-descriptions-item label="租户编码">
            {{ detailFormData.code }}
          </el-descriptions-item>
          <el-descriptions-item label="租户简称">
            {{ detailFormData.short_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="租户类型">
            <el-tag v-if="detailFormData.tenant_type === 0" type="primary">企业</el-tag>
            <el-tag v-else-if="detailFormData.tenant_type === 1" type="success">政府</el-tag>
            <el-tag v-else-if="detailFormData.tenant_type === 2" type="warning">学校</el-tag>
            <el-tag v-else-if="detailFormData.tenant_type === 3" type="info">医院</el-tag>
            <el-tag v-else-if="detailFormData.tenant_type === 4" type="">其他</el-tag>
            <el-tag v-else type="danger">未知</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="联系人">
            {{ detailFormData.contact_person || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="联系电话">
            {{ detailFormData.contact_phone || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="联系邮箱" :span="2">
            {{ detailFormData.contact_email || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="地址" :span="2">
            {{ detailFormData.address || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="detailFormData.is_active ? 'success' : 'danger'">
              {{ detailFormData.is_active ? "启用" : "停用" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ detailFormData.created_time }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间" :span="2">
            {{ detailFormData.updated_time }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ detailFormData.description || '-' }}
          </el-descriptions-item>
        </el-descriptions>
      </template>
      <!-- 新增、编辑表单 -->
      <template v-else>
        <el-form
          ref="dataFormRef"
          :model="formData"
          :rules="rules"
          label-suffix=":"
          label-width="100px"
          label-position="right"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="租户名称" prop="name">
                <el-input v-model="formData.name" placeholder="请输入租户名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="租户编码" prop="code">
                <el-input v-model="formData.code" placeholder="请输入租户编码" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="租户简称" prop="short_name">
                <el-input v-model="formData.short_name" placeholder="请输入租户简称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="租户类型" prop="tenant_type">
                <el-select v-model="formData.tenant_type" placeholder="请选择租户类型" style="width: 100%">
                  <el-option :value="0" label="企业" />
                  <el-option :value="1" label="政府" />
                  <el-option :value="2" label="学校" />
                  <el-option :value="3" label="医院" />
                  <el-option :value="4" label="其他" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="联系人" prop="contact_person">
                <el-input v-model="formData.contact_person" placeholder="请输入联系人" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系电话" prop="contact_phone">
                <el-input v-model="formData.contact_phone" placeholder="请输入联系电话" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="联系邮箱" prop="contact_email">
                <el-input v-model="formData.contact_email" placeholder="请输入联系邮箱" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="is_active">
                <el-radio-group v-model="formData.is_active">
                  <el-radio :value="true">启用</el-radio>
                  <el-radio :value="false">停用</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="地址" prop="address">
            <el-input v-model="formData.address" placeholder="请输入地址" />
          </el-form-item>
          <el-form-item label="备注" prop="description">
            <el-input
              v-model="formData.description"
              :rows="4"
              :maxlength="500"
              show-word-limit
              type="textarea"
              placeholder="请输入备注"
            />
          </el-form-item>
        </el-form>
      </template>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseDialog">取 消</el-button>
          <el-button v-if="dialogVisible.type !== 'detail'" type="primary" @click="handleSubmit">
            确 定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Tenant",
  inheritAttrs: false,
});

import { ElMessage, ElMessageBox } from "element-plus";
import TenantAPI, { TenantTable, TenantForm, TenantUpdateForm, TenantPageQuery } from "@/api/module_system/tenant";
import { QuestionFilled } from "@element-plus/icons-vue";

const queryFormRef = ref();
const dataFormRef = ref();
const selectIds = ref<number[]>([]);
const loading = ref(false);
const total = ref(0);

// 分页表单
const pageTableData = ref<TenantTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "name", label: "租户名称", show: true },
  { prop: "code", label: "租户编码", show: true },
  { prop: "short_name", label: "租户简称", show: true },
  { prop: "tenant_type", label: "租户类型", show: true },
  { prop: "contact_person", label: "联系人", show: true },
  { prop: "contact_phone", label: "联系电话", show: true },
  { prop: "is_active", label: "状态", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "operation", label: "操作", show: true },
]);

// 详情表单
const detailFormData = ref<TenantTable>({} as TenantTable);

const queryFormData = reactive<TenantPageQuery>({
  page_no: 1,
  page_size: 10,
  name: undefined,
  code: undefined,
  tenant_type: undefined,
  is_active: undefined,
  status: undefined,
});

// 新增、编辑表单
const formData = reactive<TenantForm>({
  name: "",
  code: "",
  short_name: undefined,
  logo: undefined,
  tenant_type: undefined,
  contact_person: undefined,
  contact_phone: undefined,
  contact_email: undefined,
  address: undefined,
  is_active: true,
  description: undefined,
});

// 弹窗状态
const dialogVisible = reactive({
  title: "",
  visible: false,
  type: "create" as "create" | "update" | "detail",
});

// 表单验证规则
const rules = reactive({
  name: [{ required: true, message: "请输入租户名称", trigger: "blur" }],
  code: [{ required: true, message: "请输入租户编码", trigger: "blur" }],
});

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await TenantAPI.listTenant(queryFormData);
    pageTableData.value = response.data.data.items;
    total.value = response.data.data.total;
  } catch (error: any) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

// 列表刷新
async function handleRefresh() {
  await loadingData();
}

// 查询（重置页码后获取数据）
async function handleQuery() {
  queryFormData.page_no = 1;
  loadingData();
}

// 行复选框选中项变化
async function handleSelectionChange(selection: any) {
  selectIds.value = selection.map((item: any) => item.id);
}

// 重置查询
async function handleResetQuery() {
  queryFormRef.value.resetFields();
  queryFormData.page_no = 1;
  loadingData();
}

// 定义初始表单数据常量
const initialFormData: TenantForm = {
  name: "",
  code: "",
  short_name: undefined,
  logo: undefined,
  tenant_type: undefined,
  contact_person: undefined,
  contact_phone: undefined,
  contact_email: undefined,
  address: undefined,
  is_active: true,
  description: undefined,
};

// 重置表单
async function resetForm() {
  if (dataFormRef.value) {
    dataFormRef.value.resetFields();
    dataFormRef.value.clearValidate();
  }
  // 完全重置 formData 为初始状态
  Object.assign(formData, initialFormData);
}

// 关闭弹窗
async function handleCloseDialog() {
  dialogVisible.visible = false;
  resetForm();
}

// 打开弹窗
async function handleOpenDialog(type: "create" | "update" | "detail", id?: number) {
  dialogVisible.type = type;
  if (id) {
    const response = await TenantAPI.detailTenant(id);
    if (type === "detail") {
      dialogVisible.title = "租户详情";
      Object.assign(detailFormData.value, response.data.data);
    } else if (type === "update") {
      dialogVisible.title = "修改租户";
      Object.assign(formData, response.data.data);
    }
  } else {
    dialogVisible.title = "新增租户";
  }
  dialogVisible.visible = true;
}

// 新增、编辑弹窗处理
async function handleSubmit() {
  // 表单校验
  dataFormRef.value.validate(async (valid: any) => {
    if (valid) {
      loading.value = true;
      try {
        if (dialogVisible.type === "update") {
          const updateData: TenantUpdateForm = {
            id: formData.id as number,
            ...formData,
          };
          await TenantAPI.updateTenant(updateData);
        } else {
          await TenantAPI.createTenant(formData);
        }
        dialogVisible.visible = false;
        resetForm();
        handleResetQuery();
        ElMessage.success("操作成功");
      } catch (error: any) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    }
  });
}

// 删除、批量删除
async function handleDelete(ids: number[]) {
  ElMessageBox.confirm("确认删除该项数据?删除前请确保该租户没有关联的用户、部门、角色等数据。", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        loading.value = true;
        await TenantAPI.deleteTenant(ids);
        handleResetQuery();
        ElMessage.success("删除成功");
      } catch (error: any) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    })
    .catch(() => {
      ElMessageBox.close();
    });
}

// 初始化
onMounted(() => {
  loadingData();
});
</script>
