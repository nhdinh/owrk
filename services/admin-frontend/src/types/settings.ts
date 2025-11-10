export type SettingType = 'STRING' | 'INTEGER' | 'BOOLEAN' | 'JSON';

export interface ModuleSetting {
  id: number;
  module_name: string;
  setting_key: string;
  setting_value: string;
  setting_type: SettingType;
  display_name: string;
  description?: string;
  category?: string;
  is_public: boolean;
  is_editable: boolean;
  default_value?: string;
  validation_rules?: string;
  created_at: string;
  updated_at: string;
  updated_by?: number;
}

export interface ModuleSettingCreate {
  module_name: string;
  setting_key: string;
  setting_value: string;
  setting_type: SettingType;
  display_name: string;
  description?: string;
  category?: string;
  is_public?: boolean;
  is_editable?: boolean;
  default_value?: string;
  validation_rules?: string;
}
