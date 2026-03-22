// --- Pagination ----------------------------------------------
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

// --- Role -----------------------------------------------------
export type ResourcePermissions = Record<string, Record<string, boolean>>;

export interface Role {
  id: string;
  name: string;
  description: string | null;
  is_system_role: boolean;
  permissions: ResourcePermissions;
  created_at: string;
  updated_at: string;
}

export interface RoleWithUsers extends Role {
  user_count: number;
}

export interface RoleCreate {
  name: string;
  description?: string;
  permissions: ResourcePermissions;
}

export interface RoleUpdate {
  name?: string;
  description?: string;
  permissions?: ResourcePermissions;
}

// --- User -----------------------------------------------------
export interface RoleBasic {
  id: string;
  name: string;
  permissions: ResourcePermissions;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  avatar_url: string | null;
  extra_data: Record<string, unknown>;
  roles: RoleBasic[];
  created_at: string;
  updated_at: string;
}

export interface UserSummary {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  avatar_url: string | null;
  created_at: string;
}

export interface UserCreate {
  email: string;
  full_name: string;
  password: string;
  is_superuser?: boolean;
  role_ids?: string[];
}

export interface UserUpdate {
  full_name?: string;
  avatar_url?: string;
}

export interface AssignRolesRequest {
  role_ids: string[];
}

// --- Nav item --------------------------------------------------------
export interface NavItem {
  label: string;
  route: string;
  icon: string;
  permission?: { resource: string; action: string };
  children?: NavItem[];
}
