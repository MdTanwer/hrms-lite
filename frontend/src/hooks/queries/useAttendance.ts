import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/services/axios';
import {
  Attendance,
  AttendanceApiResponse,
  AttendanceCreateDTO,
  AttendanceFilterParams,
  EmployeeAttendanceStats,
  EmployeeAttendanceStatsApiResponse,
} from '@/types/attendance';
import { PaginatedResponse } from '@/types/employee';
import { getApiErrorMessage, handleApiError, handleApiSuccess } from '@/utils/apiErrorHandler';

const ATTENDANCE_ENDPOINT = '/api/v1/attendance';

// Query keys
export const attendanceKeys = {
  all: ['attendance'] as const,
  lists: () => [...attendanceKeys.all, 'list'] as const,
  list: (filters: AttendanceFilterParams) => [...attendanceKeys.lists(), filters] as const,
  employee: (employeeId: string) => [...attendanceKeys.all, 'employee', employeeId] as const,
  employeeStats: (employeeId: string, startDate: string, endDate: string) =>
    [...attendanceKeys.all, 'employeeStats', employeeId, startDate, endDate] as const,
};

/**
 * Hook to fetch attendance (GET /attendance) with filters matching backend:
 * skip, limit, employee_id, start_date, end_date, status
 */
export const useEmployeeAttendance = (
  employeeId: string,
  params?: { start_date?: string; end_date?: string; skip?: number; limit?: number; status?: string },
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: [...attendanceKeys.employee(employeeId), params],
    queryFn: async () => {
      const res = await apiClient.get<PaginatedResponse<Attendance>>(ATTENDANCE_ENDPOINT, {
        params: { employee_id: employeeId, ...params },
      });
      return res.data;
    },
    enabled: enabled && !!employeeId,
  });
};

/**
 * Hook to fetch employee attendance stats for date range (GET /attendance/employee/{id}/stats).
 * Optimized: single aggregation on backend, no list fetch needed for stats.
 */
export const useEmployeeAttendanceStats = (
  employeeId: string,
  startDate: string,
  endDate: string,
  enabled: boolean = true
) => {
  return useQuery({
    queryKey: attendanceKeys.employeeStats(employeeId, startDate, endDate),
    queryFn: async (): Promise<EmployeeAttendanceStats> => {
      const res = await apiClient.get<EmployeeAttendanceStatsApiResponse>(
        `${ATTENDANCE_ENDPOINT}/employee/${encodeURIComponent(employeeId)}/stats`,
        { params: { start_date: startDate, end_date: endDate } }
      );
      if (res.data?.data != null) return res.data.data;
      return res.data as unknown as EmployeeAttendanceStats;
    },
    enabled: enabled && !!employeeId && !!startDate && !!endDate,
  });
};

/**
 * Hook to mark attendance (POST /api/v1/attendance).
 * Backend returns APIResponse<AttendanceInDB>; we unwrap and invalidate lists.
 */
export const useMarkAttendance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: AttendanceCreateDTO): Promise<Attendance> => {
      const res = await apiClient.post<AttendanceApiResponse>(ATTENDANCE_ENDPOINT, data);
      const body = res.data;
      if (body?.data != null) return body.data;
      return body as unknown as Attendance;
    },
    onSuccess: (newAttendance: Attendance) => {
      const employeeId = newAttendance.employee_id ?? newAttendance.employeeId ?? '';
      queryClient.invalidateQueries({ queryKey: attendanceKeys.lists() });
      queryClient.invalidateQueries({ queryKey: attendanceKeys.employee(employeeId) });
      queryClient.invalidateQueries({ queryKey: [...attendanceKeys.all, 'employeeStats', employeeId] });
      handleApiSuccess('Attendance marked successfully!');
    },
    onError: (error) => {
      const message = getApiErrorMessage(error);
      if (message === 'Attendance date cannot be in the future') return;
      handleApiError(error);
    },
  });
};

