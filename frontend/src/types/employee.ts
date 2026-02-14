export interface Employee {
  employee_id?: string;
  full_name?: string;
  email: string;
  department: string;
  position?: string;
  id?: string;
  _id?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
}

/** Payload for creating an employee; backend accepts camelCase. */
export interface CreateEmployeePayload {
  employeeId: string;
  fullName: string;
  email: string;
  department: string;
  position?: string;
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
