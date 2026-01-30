import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { attendanceService, AttendanceCreateDTO, AttendanceUpdateDTO, AttendanceFilterParams } from '@/services/api';
import { handleApiError, handleApiSuccess } from '@/utils/apiErrorHandler';

// Query keys
export const attendanceKeys = {
  all: ['attendance'] as const,
  lists: () => [...attendanceKeys.all, 'list'] as const,
  list: (filters: AttendanceFilterParams) => [...attendanceKeys.lists(), filters] as const,
  details: () => [...attendanceKeys.all, 'detail'] as const,
  detail: (id: string) => [...attendanceKeys.details(), id] as const,
  employee: (employeeId: string) => [...attendanceKeys.all, 'employee', employeeId] as const,
  summary: (employeeId: string, startDate?: string, endDate?: string) =>
    [...attendanceKeys.all, 'summary', employeeId, startDate, endDate] as const,
  stats: (date: string) => [...attendanceKeys.all, 'stats', date] as const,
};

/**
 * Hook to fetch attendance records with filtering
 */
export const useAttendance = (params?: AttendanceFilterParams) => {
  return useQuery({
    queryKey: attendanceKeys.list(params || {}),
    queryFn: () => attendanceService.getAttendance(params),
  });
};

/**
 * Hook to fetch attendance for specific employee
 */
export const useEmployeeAttendance = (
  employeeId: string,
  params?: { start_date?: string; end_date?: string },
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: [...attendanceKeys.employee(employeeId), params],
    queryFn: () => attendanceService.getByEmployee(employeeId, params),
    enabled: enabled && !!employeeId,
  });
};

/**
 * Hook to fetch attendance summary for employee
 */
export const useEmployeeAttendanceSummary = (
  employeeId: string,
  startDate?: string,
  endDate?: string,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: attendanceKeys.summary(employeeId, startDate, endDate),
    queryFn: () => attendanceService.getEmployeeSummary(employeeId, {
      start_date: startDate,
      end_date: endDate,
    }),
    enabled: enabled && !!employeeId,
  });
};

/**
 * Hook to fetch attendance for specific date
 */
export const useAttendanceByDate = (date: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...attendanceKeys.all, 'date', date],
    queryFn: () => attendanceService.getByDate(date),
    enabled: enabled && !!date,
  });
};

/**
 * Hook to mark attendance
 */
export const useMarkAttendance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AttendanceCreateDTO) => attendanceService.markAttendance(data),
    onSuccess: (newAttendance) => {
      // Invalidate all attendance lists
      queryClient.invalidateQueries({ queryKey: attendanceKeys.lists() });
      
      // Invalidate employee-specific attendance
      queryClient.invalidateQueries({
        queryKey: attendanceKeys.employee(newAttendance.employee_id),
      });
      
      // Invalidate date-specific attendance
      queryClient.invalidateQueries({
        queryKey: [...attendanceKeys.all, 'date', newAttendance.date],
      });
      
      // Invalidate summary
      queryClient.invalidateQueries({
        queryKey: [...attendanceKeys.all, 'summary', newAttendance.employee_id],
      });
      
      handleApiSuccess('Attendance marked successfully!');
    },
    onError: (error) => {
      handleApiError(error);
    },
  });
};

/**
 * Hook to bulk mark attendance
 */
export const useBulkMarkAttendance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AttendanceCreateDTO[]) => attendanceService.bulkMarkAttendance(data),
    onSuccess: () => {
      // Invalidate all attendance-related queries
      queryClient.invalidateQueries({ queryKey: attendanceKeys.all });
      
      handleApiSuccess('Bulk attendance marked successfully!');
    },
    onError: (error) => {
      handleApiError(error);
    },
  });
};

/**
 * Hook to update attendance
 */
export const useUpdateAttendance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: AttendanceUpdateDTO }) =>
      attendanceService.updateAttendance(id, data),
    onSuccess: (updatedAttendance) => {
      // Update in cache
      queryClient.setQueryData(
        attendanceKeys.detail(updatedAttendance.id),
        updatedAttendance
      );
      
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: attendanceKeys.lists() });
      
      handleApiSuccess('Attendance updated successfully!');
    },
    onError: (error) => {
      handleApiError(error);
    },
  });
};

/**
 * Hook to delete attendance
 */
export const useDeleteAttendance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => attendanceService.deleteAttendance(id),
    onSuccess: (_, id) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: attendanceKeys.detail(id) });
      
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: attendanceKeys.lists() });
      
      handleApiSuccess('Attendance deleted successfully!');
    },
    onError: (error) => {
      handleApiError(error);
    },
  });
};
