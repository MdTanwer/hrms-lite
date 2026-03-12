import apiClient from '@/services/axios';
import {
  Employee,
  CreateEmployeePayload,
  EmployeeFilterParams,
  APIResponse,
  EmployeeListResponse,
} from '@/types/employee';

class EmployeeService {
  private readonly endpoint = '/api/v1/employees';

  /**
   * Get employees with advanced filtering
   */
  async getEmployees(params?: EmployeeFilterParams): Promise<EmployeeListResponse> {
    const response = await apiClient.get<EmployeeListResponse>(this.endpoint, { params });
    return response.data;
  }

  /**
   * Get employee by employee_id (e.g., EMP001)
   */
  async getByEmployeeId(employeeId: string): Promise<Employee> {
    const response = await apiClient.get<APIResponse<Employee>>(`${this.endpoint}/${employeeId}`);
    return response.data.data;
  }

  /**
   * Create new employee (backend accepts camelCase).
   */
  async createEmployee(data: CreateEmployeePayload): Promise<Employee> {
    const response = await apiClient.post<APIResponse<Employee>>(this.endpoint, data);
    return response.data.data;
  }

  /**
   * Delete employee
   */
  async deleteEmployee(employeeId: string): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.delete<{ success: boolean; message: string }>(`${this.endpoint}/${employeeId}`);
    return response.data;
  }

  /**
   * Get employees by department
   */
  async getByDepartment(
    department: string,
    params?: { skip?: number; limit?: number }
  ): Promise<EmployeeListResponse> {
    const response = await apiClient.get<EmployeeListResponse>(
      `${this.endpoint}/department/${department}`,
      { params }
    );
    return response.data;
  }

  /**
   * Search employees
   */
  async searchEmployees(
    searchTerm: string,
    params?: { skip?: number; limit?: number }
  ): Promise<EmployeeListResponse> {
    const response = await apiClient.get<EmployeeListResponse>(
      this.endpoint,
      { params: { search: searchTerm, ...params } }
    );
    return response.data;
  }
}

// Export singleton instance
export const employeeService = new EmployeeService();

// Export type for the service
export type EmployeeServiceType = typeof employeeService;
