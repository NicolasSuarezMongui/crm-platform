// ─── Field types ─────────────────────────────────────────────
export type FieldType =
  | 'text'
  | 'long_text'
  | 'integer'
  | 'decimal'
  | 'boolean'
  | 'date'
  | 'datetime'
  | 'email'
  | 'phone'
  | 'url'
  | 'select'
  | 'multi_select'
  | 'relation';

export interface SelectOption {
  value: string;
  label: string;
  color?: string;
}

export interface FieldOptions {
  options?: SelectOption[]; // SELECT, MULTI_SELECT
  target_object_type?: string; // RELATION
  max_length?: number; // TEXT
  pattern?: string; // TEXT
}

// ─── Field definition ────────────────────────────────────────
export interface FieldDefinition {
  id: string;
  api_name: string;
  label: string;
  field_type: FieldType;
  is_required: boolean;
  is_system: boolean;
  is_searchable: boolean;
  sort_order: number;
  options: FieldOptions;
}

export interface FieldDefinitionCreate {
  api_name: string;
  label: string;
  field_type: FieldType;
  is_required?: boolean;
  is_searchable?: boolean;
  sort_order?: number;
  options?: FieldOptions;
}

// ─── Object type ─────────────────────────────────────────────
export interface ObjectType {
  id: string;
  api_name: string;
  label: string;
  label_plural: string;
  description: string | null;
  icon: string | null;
  color: string | null;
  is_system: boolean;
  layout_config: Record<string, unknown>;
  field_definitions: FieldDefinition[];
  created_at: string;
  updated_at: string;
}

export interface ObjectTypeSummary {
  id: string;
  api_name: string;
  label: string;
  label_plural: string;
  icon: string | null;
  color: string | null;
  is_system: boolean;
}

export interface ObjectTypeCreate {
  api_name: string;
  label: string;
  label_plural: string;
  description?: string;
  icon?: string;
  color?: string;
  fields?: FieldDefinitionCreate[];
}

export interface ObjectTypeUpdate {
  label?: string;
  label_plural?: string;
  description?: string;
  icon?: string;
  color?: string;
  layout_config?: Record<string, unknown>;
}

// ─── Record ──────────────────────────────────────────────────
export interface CrmRecord {
  id: string;
  object_type_id: string;
  name: string;
  stage: string | null;
  owner_id: string | null;
  data: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface RecordCreate {
  name: string;
  stage?: string;
  owner_id?: string;
  data: Record<string, unknown>;
}

export interface RecordUpdate {
  name?: string;
  stage?: string;
  owner_id?: string;
  data?: Record<string, unknown>;
}

// Field type metadata for UI
export const FIELD_TYPE_LABELS: Record<FieldType, string> = {
  text: 'Texto',
  long_text: 'Texto largo',
  integer: 'Número entero',
  decimal: 'Decimal',
  boolean: 'Sí / No',
  date: 'Fecha',
  datetime: 'Fecha y hora',
  email: 'Email',
  phone: 'Teléfono',
  url: 'URL',
  select: 'Selección única',
  multi_select: 'Selección múltiple',
  relation: 'Relación',
};
