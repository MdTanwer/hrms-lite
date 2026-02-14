import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { employeeService, EmployeeFilterParams } from '@/services/api';
import { handleApiError, handleApiSuccess } from '@/utils/apiErrorHandler';
import { CreateEmployeePayload, EmployeeListResponse } from '@/types/employee';

// Query keys for cache management
export const employeeKeys = {
  all: ['employees'] as const,
  lists: () => [...employeeKeys.all, 'list'] as const,
  list: (filters: EmployeeFilterParams) => [...employeeKeys.lists(), filters] as const,
  details: () => [...employeeKeys.all, 'detail'] as const,
  detail: (id: string) => [...employeeKeys.details(), id] as const,
};

/**
 * Hook to fetch all employees with filtering
 */
export const useEmployees = (params?: EmployeeFilterParams) => {
  return useQuery({
    queryKey: employeeKeys.list(params || {}),
    queryFn: () => employeeService.getEmployees(params),
    select: (data: EmployeeListResponse) => data, // Return the full response
  });
};

/**
 * Hook to fetch single employee by employee_id
 */
export const useEmployee = (employeeId: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: employeeKeys.detail(employeeId),
    queryFn: () => employeeService.getByEmployeeId(employeeId),
    enabled: enabled && !!employeeId, // Only run if enabled and employeeId exists
  });
};

/**
 * Hook to create new employee
 */
export const useCreateEmployee = (onSuccess?: () => void) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateEmployeePayload) => employeeService.createEmployee(data),
    onSuccess: () => {
      // Show success message
      handleApiSuccess('Employee created successfully!');
      
      // Invalidate and refetch employee lists
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
      
      // Call custom success callback (to close modal, etc.)
      if (onSuccess) {
        onSuccess();
      }
    },
    onError: (error) => {
      handleApiError(error);
    },
  });
};




/**
 * Hook to delete employee
 */
export const useDeleteEmployee = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (employeeId: string) => employeeService.deleteEmployee(employeeId),
    onSuccess: (_, employeeId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: employeeKeys.detail(employeeId) });
      
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: employeeKeys.lists() });
      
      handleApiSuccess('Employee deleted successfully!');
    },
    onError: (error) => {
      handleApiError(error);
    },
  });
};

/**
 * Hook to search employees
 */
export const useSearchEmployees = (searchTerm: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...employeeKeys.lists(), 'search', searchTerm],
    queryFn: () => employeeService.searchEmployees(searchTerm),
    enabled: enabled && searchTerm.length > 0,
    staleTime: 1000 * 30, // Search results stale after 30 seconds
  });
};
