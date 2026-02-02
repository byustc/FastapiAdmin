import request from "@/utils/request";

const API_PATH = "/system/tenant";

const TenantAPI = {
  listTenant(query?: TenantPageQuery) {
    return request<ApiResponse<PageResult<TenantTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  detailTenant(id: number) {
    return request<ApiResponse<TenantTable>>({
      url: `${API_PATH}/detail/${id}`,
      method: "get",
    });
  },

  createTenant(body: TenantForm) {
    return request<ApiResponse<TenantTable>>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  updateTenant(body: TenantUpdateForm) {
    return request<ApiResponse<TenantTable>>({
      url: `${API_PATH}/update`,
      method: "put",
      data: body,
    });
  },

  deleteTenant(ids: number[]) {
    return request<ApiResponse>({
      url: `${API_PATH}/delete`,
      method: "delete",
      data: ids,
    });
  },

  getAllTenants() {
    return request<ApiResponse<TenantTable[]>>({
      url: `${API_PATH}/all`,
      method: "get",
    });
  },
};

export default TenantAPI;

export interface TenantPageQuery extends PageQuery {
  name?: string;
  code?: string;
  tenant_type?: number;
  is_active?: boolean;
  status?: string;
}

export interface TenantTable extends BaseType {
  id: number;
  uuid: string;
  name: string;
  code: string;
  short_name?: string;
  logo?: string;
  tenant_type?: number;
  contact_person?: string;
  contact_phone?: string;
  contact_email?: string;
  address?: string;
  is_active: boolean;
  status: string;
  description?: string;
  created_time: string;
  updated_time: string;
}

export interface TenantForm {
  name: string;
  code: string;
  short_name?: string;
  logo?: string;
  tenant_type?: number;
  contact_person?: string;
  contact_phone?: string;
  contact_email?: string;
  address?: string;
  is_active: boolean;
  description?: string;
}

export interface TenantUpdateForm extends TenantForm {
  id: number;
}
