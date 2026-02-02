import request from "@/utils/request";

const API_PATH = "/system/share";

const ShareAPI = {
  listShare(query?: SharePageQuery) {
    return request<ApiResponse<PageResult<ShareTable[]>>>({
      url: `${API_PATH}/list`,
      method: "get",
      params: query,
    });
  },

  createShare(body: ShareForm) {
    return request<ApiResponse<ShareTable>>({
      url: `${API_PATH}/create`,
      method: "post",
      data: body,
    });
  },

  revokeShare(shareId: number) {
    return request<ApiResponse>({
      url: `${API_PATH}/revoke/${shareId}`,
      method: "delete",
    });
  },

  copyData(body: DataCopyForm) {
    return request<ApiResponse<DataCopyResult>>({
      url: `${API_PATH}/copy`,
      method: "post",
      data: body,
    });
  },
};

export default ShareAPI;

export interface SharePageQuery extends PageQuery {
  resource_type?: string;
  target_tenant_id?: number;
  share_type?: number;
  status?: string;
}

export interface ShareTable extends BaseType {
  id: number;
  uuid: string;
  resource_type: string;
  resource_id: number;
  target_tenant_id: number;
  target_tenant_name?: string;
  share_type: number;
  status: string;
  expire_time?: string;
  remark?: string;
  created_time: string;
  updated_time: string;
}

export interface ShareForm {
  resource_type: string;
  resource_id: number;
  target_tenant_id: number;
  share_type: 1 | 2;
  expire_time?: string;
  remark?: string;
}

export interface DataCopyForm {
  resource_type: string;
  resource_ids: number[];
  target_tenant_id: number;
}

export interface DataCopyResult {
  copied_count: number;
  target_tenant_id: number;
  id_mapping: Record<number, number>;
}
