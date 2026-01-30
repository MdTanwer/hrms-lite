// Export services
export { employeeService } from './employeeService';
export { attendanceService } from './attendanceService';
export { dashboardService } from './dashboardService';

// Export types from employee types directory
export type { 
  EmployeeFilterParams, 
  EmployeeStats,
  APIResponse,
  EmployeeListResponse,
  PaginationParams,
  PaginatedResponse
} from '@/types/employee';

// Export other service types
export type { AttendanceServiceType, AttendanceCreateDTO, AttendanceUpdateDTO, AttendanceFilterParams, AttendanceSummary, AttendanceStats } from './attendanceService';
export type { DashboardServiceType, DashboardOverview, AttendanceTrend, DepartmentStats } from './dashboardService';

// Re-export axios client for custom requests
export { default as apiClient } from '../axios';
