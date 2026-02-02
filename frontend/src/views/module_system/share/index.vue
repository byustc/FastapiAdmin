<!-- 数据分享管理 -->
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
        <el-form-item prop="resource_type" label="资源类型">
          <el-input v-model="queryFormData.resource_type" placeholder="请输入资源类型(表名)" clearable />
        </el-form-item>
        <el-form-item prop="target_tenant_id" label="目标租户">
          <el-select
            v-model="queryFormData.target_tenant_id"
            placeholder="请选择目标租户"
            style="width: 167.5px"
            clearable
            filterable
          >
            <el-option
              v-for="tenant in allTenants"
              :key="tenant.id"
              :label="tenant.name"
              :value="tenant.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item prop="share_type" label="分享类型">
          <el-select
            v-model="queryFormData.share_type"
            placeholder="请选择分享类型"
            style="width: 167.5px"
            clearable
          >
            <el-option :value="1" label="仅查看" />
            <el-option :value="2" label="查看和编辑" />
          </el-select>
        </el-form-item>
        <el-form-item prop="status" label="状态">
          <el-select
            v-model="queryFormData.status"
            placeholder="请选择状态"
            style="width: 167.5px"
            clearable
          >
            <el-option value="0" label="生效" />
            <el-option value="1" label="失效" />
          </el-select>
        </el-form-item>
        <!-- 查询、重置按钮 -->
        <el-form-item class="search-buttons">
          <el-button
            v-hasPerm="['system:share:query']"
            type="primary"
            icon="search"
            native-type="submit"
          >
            查询
          </el-button>
          <el-button
            v-hasPerm="['system:share:query']"
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
            <el-tooltip content="数据分享管理跨租户的数据分享。">
              <QuestionFilled class="w-4 h-4 mx-1" />
            </el-tooltip>
            数据分享列表
          </span>
        </div>
      </template>

      <!-- 功能区域 -->
      <div class="data-table__toolbar">
        <div class="data-table__toolbar--left">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['system:share:create']"
                type="success"
                icon="plus"
                @click="handleOpenCreateDialog"
              >
                新增分享
              </el-button>
            </el-col>
            <el-col :span="1.5">
              <el-button
                v-hasPerm="['system:share:copy']"
                type="primary"
                icon="copy-document"
                :disabled="selectIds.length === 0"
                @click="handleOpenCopyDialog"
              >
                复制数据
              </el-button>
            </el-col>
          </el-row>
        </div>
        <div class="data-table__toolbar--right">
          <el-row :gutter="10">
            <el-col :span="1.5">
              <el-tooltip content="刷新">
                <el-button
                  v-hasPerm="['system:share:query']"
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
          v-if="tableColumns.find((col) => col.prop === 'resource_type')?.show"
          key="resource_type"
          label="资源类型"
          prop="resource_type"
          min-width="150"
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'resource_id')?.show"
          key="resource_id"
          label="资源ID"
          prop="resource_id"
          min-width="100"
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'target_tenant_name')?.show"
          key="target_tenant_name"
          label="目标租户"
          prop="target_tenant_name"
          min-width="150"
          show-overflow-tooltip
        />
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'share_type')?.show"
          key="share_type"
          label="分享类型"
          prop="share_type"
          min-width="120"
        >
          <template #default="scope">
            <el-tag v-if="scope.row.share_type === 1" type="info">仅查看</el-tag>
            <el-tag v-else-if="scope.row.share_type === 2" type="success">查看和编辑</el-tag>
            <el-tag v-else type="danger">未知</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'status')?.show"
          key="status"
          label="状态"
          prop="status"
          min-width="80"
        >
          <template #default="scope">
            <el-tag :type="scope.row.status === '0' ? 'success' : 'danger'">
              {{ scope.row.status === "0" ? "生效" : "失效" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          v-if="tableColumns.find((col) => col.prop === 'expire_time')?.show"
          key="expire_time"
          label="过期时间"
          prop="expire_time"
          min-width="180"
        >
          <template #default="scope">
            {{ scope.row.expire_time || '永久' }}
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
          min-width="150"
        >
          <template #default="scope">
            <el-button
              v-hasPerm="['system:share:revoke']"
              type="danger"
              size="small"
              link
              icon="delete"
              @click="handleRevokeShare(scope.row.id)"
            >
              撤销分享
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

    <!-- 创建分享弹窗 -->
    <el-dialog
      v-model="createDialogVisible"
      title="创建数据分享"
      width="600px"
      @close="handleCloseCreateDialog"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-suffix=":"
        label-width="100px"
      >
        <el-form-item label="资源类型" prop="resource_type">
          <el-input v-model="createForm.resource_type" placeholder="请输入资源类型(表名)" />
          <div class="text-gray-500 text-xs mt-1">例如：sys_user, sys_role 等</div>
        </el-form-item>
        <el-form-item label="资源ID" prop="resource_id">
          <el-input-number v-model="createForm.resource_id" :min="1" style="width: 100%" />
          <div class="text-gray-500 text-xs mt-1">要分享的数据记录ID</div>
        </el-form-item>
        <el-form-item label="目标租户" prop="target_tenant_id">
          <el-select
            v-model="createForm.target_tenant_id"
            placeholder="请选择目标租户"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="tenant in allTenants"
              :key="tenant.id"
              :label="tenant.name"
              :value="tenant.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分享类型" prop="share_type">
          <el-radio-group v-model="createForm.share_type">
            <el-radio :value="1">仅查看</el-radio>
            <el-radio :value="2">查看和编辑</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="过期时间" prop="expire_time">
          <el-date-picker
            v-model="createForm.expire_time"
            type="datetime"
            placeholder="选择过期时间（不选则永久）"
            style="width: 100%"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="分享说明" prop="remark">
          <el-input
            v-model="createForm.remark"
            :rows="4"
            :maxlength="500"
            show-word-limit
            type="textarea"
            placeholder="请输入分享说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseCreateDialog">取 消</el-button>
          <el-button type="primary" @click="handleSubmitCreate">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 复制数据弹窗 -->
    <el-dialog
      v-model="copyDialogVisible"
      title="复制数据到目标租户"
      width="600px"
      @close="handleCloseCopyDialog"
    >
      <el-alert
        title="复制说明"
        type="info"
        :closable="false"
        class="mb-4"
      >
        <ul class="text-sm">
          <li>仅复制主表数据，不复制关联数据</li>
          <li>复制后的数据完全独立，与源数据无关联</li>
          <li>返回新旧ID映射关系</li>
        </ul>
      </el-alert>
      <el-form
        ref="copyFormRef"
        :model="copyForm"
        :rules="copyRules"
        label-suffix=":"
        label-width="100px"
      >
        <el-form-item label="资源类型" prop="resource_type">
          <el-input v-model="copyForm.resource_type" placeholder="请输入资源类型(表名)" />
        </el-form-item>
        <el-form-item label="资源ID列表" prop="resource_ids">
          <el-input
            v-model="resourceIdsText"
            :rows="4"
            type="textarea"
            placeholder="请输入资源ID列表，多个ID用逗号分隔，例如：1,2,3"
          />
          <div class="text-gray-500 text-xs mt-1">多个ID用逗号分隔</div>
        </el-form-item>
        <el-form-item label="目标租户" prop="target_tenant_id">
          <el-select
            v-model="copyForm.target_tenant_id"
            placeholder="请选择目标租户"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="tenant in allTenants"
              :key="tenant.id"
              :label="tenant.name"
              :value="tenant.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleCloseCopyDialog">取 消</el-button>
          <el-button type="primary" @click="handleSubmitCopy">确 定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 复制结果弹窗 -->
    <el-dialog
      v-model="copyResultDialogVisible"
      title="复制结果"
      width="700px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="复制数量">
          {{ copyResult.copied_count }}
        </el-descriptions-item>
        <el-descriptions-item label="目标租户ID">
          {{ copyResult.target_tenant_id }}
        </el-descriptions-item>
      </el-descriptions>
      <div class="mt-4">
        <div class="font-bold mb-2">ID映射关系（旧ID -> 新ID）</div>
        <el-scrollbar max-height="300px">
          <div class="bg-gray-50 p-2 rounded">
            <div v-for="(newId, oldId) in copyResult.id_mapping" :key="oldId" class="text-sm py-1">
              <span class="font-mono">ID: {{ oldId }} &rarr; {{ newId }}</span>
            </div>
          </div>
        </el-scrollbar>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button type="primary" @click="copyResultDialogVisible = false">关 闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
defineOptions({
  name: "Share",
  inheritAttrs: false,
});

import { ElMessage, ElMessageBox } from "element-plus";
import ShareAPI, {
  ShareTable,
  ShareForm,
  SharePageQuery,
  DataCopyForm,
  DataCopyResult,
} from "@/api/module_system/share";
import TenantAPI from "@/api/module_system/tenant";
import type { TenantTable } from "@/api/module_system/tenant";
import { QuestionFilled } from "@element-plus/icons-vue";

const queryFormRef = ref();
const createFormRef = ref();
const copyFormRef = ref();
const selectIds = ref<number[]>([]);
const selectionRows = ref<any[]>([]);
const loading = ref(false);
const total = ref(0);

// 分页表单
const pageTableData = ref<ShareTable[]>([]);

// 所有租户
const allTenants = ref<TenantTable[]>([]);

// 表格列配置
const tableColumns = ref([
  { prop: "selection", label: "选择框", show: true },
  { prop: "index", label: "序号", show: true },
  { prop: "resource_type", label: "资源类型", show: true },
  { prop: "resource_id", label: "资源ID", show: true },
  { prop: "target_tenant_name", label: "目标租户", show: true },
  { prop: "share_type", label: "分享类型", show: true },
  { prop: "status", label: "状态", show: true },
  { prop: "expire_time", label: "过期时间", show: true },
  { prop: "created_time", label: "创建时间", show: true },
  { prop: "operation", label: "操作", show: true },
]);

const queryFormData = reactive<SharePageQuery>({
  page_no: 1,
  page_size: 10,
  resource_type: undefined,
  target_tenant_id: undefined,
  share_type: undefined,
  status: undefined,
});

// 创建分享表单
const createDialogVisible = ref(false);
const createForm = reactive<ShareForm>({
  resource_type: "",
  resource_id: 1,
  target_tenant_id: undefined as any,
  share_type: 1,
  expire_time: undefined,
  remark: undefined,
});

const createRules = reactive({
  resource_type: [{ required: true, message: "请输入资源类型", trigger: "blur" }],
  resource_id: [{ required: true, message: "请输入资源ID", trigger: "blur" }],
  target_tenant_id: [{ required: true, message: "请选择目标租户", trigger: "change" }],
  share_type: [{ required: true, message: "请选择分享类型", trigger: "change" }],
});

// 复制数据表单
const copyDialogVisible = ref(false);
const copyResultDialogVisible = ref(false);
const copyForm = reactive<DataCopyForm>({
  resource_type: "",
  resource_ids: [],
  target_tenant_id: undefined as any,
});
const resourceIdsText = ref("");
const copyResult = reactive<DataCopyResult>({
  copied_count: 0,
  target_tenant_id: 0,
  id_mapping: {},
});

const copyRules = reactive({
  resource_type: [{ required: true, message: "请输入资源类型", trigger: "blur" }],
  resource_ids: [
    {
      required: true,
      message: "请输入资源ID列表",
      trigger: "change",
      validator: (rule: any, value: any, callback: any) => {
        if (!resourceIdsText.value || resourceIdsText.value.trim() === "") {
          callback(new Error("请输入资源ID列表"));
        } else {
          const ids = resourceIdsText.value.split(",").map((id) => parseInt(id.trim()));
          if (ids.some((id) => isNaN(id))) {
            callback(new Error("ID格式不正确"));
          } else {
            callback();
          }
        }
      },
    },
  ],
  target_tenant_id: [{ required: true, message: "请选择目标租户", trigger: "change" }],
});

// 加载表格数据
async function loadingData() {
  loading.value = true;
  try {
    const response = await ShareAPI.listShare(queryFormData);
    pageTableData.value = response.data.data.items;
    total.value = response.data.data.total;
  } catch (error: any) {
    console.error(error);
  } finally {
    loading.value = false;
  }
}

// 加载所有租户
async function loadAllTenants() {
  try {
    const response = await TenantAPI.getAllTenants();
    allTenants.value = response.data.data;
  } catch (error: any) {
    console.error(error);
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
  selectionRows.value = selection;
}

// 重置查询
async function handleResetQuery() {
  queryFormRef.value.resetFields();
  queryFormData.page_no = 1;
  loadingData();
}

// 打开创建分享弹窗
async function handleOpenCreateDialog() {
  createDialogVisible.value = true;
}

// 关闭创建分享弹窗
async function handleCloseCreateDialog() {
  createDialogVisible.value = false;
  createFormRef.value?.resetFields();
  Object.assign(createForm, {
    resource_type: "",
    resource_id: 1,
    target_tenant_id: undefined,
    share_type: 1,
    expire_time: undefined,
    remark: undefined,
  });
}

// 提交创建分享
async function handleSubmitCreate() {
  createFormRef.value.validate(async (valid: any) => {
    if (valid) {
      loading.value = true;
      try {
        await ShareAPI.createShare(createForm);
        ElMessage.success("创建成功");
        handleCloseCreateDialog();
        handleResetQuery();
      } catch (error: any) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    }
  });
}

// 撤销分享
async function handleRevokeShare(shareId: number) {
  ElMessageBox.confirm("确认撤销该分享？", "警告", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    type: "warning",
  })
    .then(async () => {
      try {
        loading.value = true;
        await ShareAPI.revokeShare(shareId);
        ElMessage.success("撤销成功");
        handleResetQuery();
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

// 打开复制数据弹窗
async function handleOpenCopyDialog() {
  if (selectionRows.value.length === 0) {
    ElMessage.warning("请先选择要复制的数据");
    return;
  }

  // 资源类型必须一致
  const resourceTypes = new Set(selectionRows.value.map((row) => row.resource_type));
  if (resourceTypes.size > 1) {
    ElMessage.warning("只能复制相同资源类型的数据");
    return;
  }

  copyForm.resource_type = selectionRows.value[0].resource_type;
  copyForm.resource_ids = selectionRows.value.map((row) => row.resource_id);
  resourceIdsText.value = copyForm.resource_ids.join(",");

  copyDialogVisible.value = true;
}

// 关闭复制数据弹窗
async function handleCloseCopyDialog() {
  copyDialogVisible.value = false;
  copyFormRef.value?.resetFields();
  resourceIdsText.value = "";
  Object.assign(copyForm, {
    resource_type: "",
    resource_ids: [],
    target_tenant_id: undefined,
  });
}

// 提交复制数据
async function handleSubmitCopy() {
  copyFormRef.value.validate(async (valid: any) => {
    if (valid) {
      // 解析资源ID列表
      copyForm.resource_ids = resourceIdsText.value
        .split(",")
        .map((id) => parseInt(id.trim()))
        .filter((id) => !isNaN(id));

      loading.value = true;
      try {
        const response = await ShareAPI.copyData(copyForm);
        Object.assign(copyResult, response.data.data);
        copyResultDialogVisible.value = true;
        handleCloseCopyDialog();
        ElMessage.success("复制成功");
      } catch (error: any) {
        console.error(error);
      } finally {
        loading.value = false;
      }
    }
  });
}

// 初始化
onMounted(() => {
  loadingData();
  loadAllTenants();
});
</script>

<style scoped>
.text-gray-500 {
  color: #6b7280;
}
.text-xs {
  font-size: 0.75rem;
}
.mt-1 {
  margin-top: 0.25rem;
}
.mt-4 {
  margin-top: 1rem;
}
.mb-2 {
  margin-bottom: 0.5rem;
}
.mb-4 {
  margin-bottom: 1rem;
}
.text-sm {
  font-size: 0.875rem;
}
.font-bold {
  font-weight: 700;
}
.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}
.bg-gray-50 {
  background-color: #f9fafb;
}
.p-2 {
  padding: 0.5rem;
}
.py-1 {
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}
.rounded {
  border-radius: 0.375rem;
}
</style>
