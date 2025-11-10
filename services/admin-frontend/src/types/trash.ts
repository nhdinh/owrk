export interface TrashItem {
  id: number;
  module_name: string;
  resource_type: string;
  resource_id: string;
  resource_name: string;
  resource_data: Record<string, any>;
  deleted_by: number;
  deleted_by_email?: string;
  deleted_at: string;
  deleted_reason?: string;
  is_restorable: boolean;
  permanent_delete_at?: string;
  restore_dependencies?: any[];
  extra_metadata?: Record<string, any>;
  restored_at?: string;
  restored_by?: number;
  restored_by_email?: string;
}

export interface TrashStats {
  total_items: number;
  by_module: Record<string, number>;
  by_type: Record<string, number>;
  restorable_count: number;
  scheduled_for_deletion: number;
  oldest_item?: string;
  newest_item?: string;
}

export interface TrashConfig {
  id: number;
  module_name: string;
  resource_type: string;
  auto_delete_days: number;
  enable_soft_delete: boolean;
  enable_restore: boolean;
  require_approval: boolean;
  cascade_delete: boolean;
}
