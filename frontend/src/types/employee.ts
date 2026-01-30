export interface Employee {
  employee_id?: string; // Backend returns employee_id
  full_name?: string; // Backend returns full_name
  email: string;
  department: string;
  position?: string;
  id?: string; // MongoDB _id
  _id?: string; // Backend returns _id
  status?: string;
  created_at?: string;
  updated_at?: string;
}

export interface EmployeeFormData {
  employee_id: string;
  full_name: string;
  email: string;
  department: string;
  position: string;
}

export interface EmployeeFilterParams {
  skip?: number;
  limit?: number;
  department?: string;
  status?: string;
  search?: string;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface EmployeeStats {
  total_employees: number;
  active_employees: number;
  inactive_employees: number;
  on_leave_employees: number;
  department_breakdown: Record<string, number>;
}

// Backend API Response Types
export interface APIResponse<T> {
  success: boolean;
  message: string;
  data: T;
  errors: null | string[];
  timestamp: string;
}

export interface EmployeeListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  data: Employee[];
}
