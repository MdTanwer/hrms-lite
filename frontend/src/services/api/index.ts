// Export services
export { employeeService } from '@/services/api/employeeService';

// Export types from employee types directory
export type {
  EmployeeFilterParams,
  APIResponse,
  EmployeeListResponse,
  PaginationParams,
  PaginatedResponse,
} from '@/types/employee';

// Export attendance types (used by hooks/pages)
export type {
  AttendanceCreateDTO,
  AttendanceFilterParams,
} from '@/types/attendance';

// Re-export axios client for custom requests
export { default as apiClient } from '@/services/axios';
