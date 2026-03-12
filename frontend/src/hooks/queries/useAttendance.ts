import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/services/axios';
import {
  Attendance,
  AttendanceCreateDTO,
  AttendanceUpdateDTO,
  AttendanceFilterParams,
  AttendanceSummary,
} from '@/types/attendance';
import { PaginatedResponse } from '@/types/employee';
import { handleApiError, handleApiSuccess } from '@/utils/apiErrorHandler';

const ATTENDANCE_ENDPOINT = '/api/v1/attendance';

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
    queryFn: async () => {
      const res = await apiClient.get<PaginatedResponse<Attendance>>(ATTENDANCE_ENDPOINT, { params });
      return res.data;
    },
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
    queryFn: async () => {
      const res = await apiClient.get<PaginatedResponse<Attendance>>(
        `${ATTENDANCE_ENDPOINT}/employee/${employeeId}`,
        { params }
      );
      return res.data;
    },
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
    queryFn: async () => {
      const res = await apiClient.get<AttendanceSummary>(
        `${ATTENDANCE_ENDPOINT}/employee/${employeeId}/summary`,
        { params: { start_date: startDate, end_date: endDate } }
      );
      return res.data;
    },
    enabled: enabled && !!employeeId,
  });
};

/**
 * Hook to fetch attendance for specific date
 */
export const useAttendanceByDate = (date: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: [...attendanceKeys.all, 'date', date],
    queryFn: async () => {
      const res = await apiClient.get<PaginatedResponse<Attendance>>(
        `${ATTENDANCE_ENDPOINT}/date/${date}`
      );
      return res.data;
    },
    enabled: enabled && !!date,
  });
};

/**
 * Hook to mark attendance
 */
export const useMarkAttendance = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: AttendanceCreateDTO) => {
      const res = await apiClient.post<Attendance>(ATTENDANCE_ENDPOINT, data);
      return res.data;
    },
    onSuccess: (newAttendance: Attendance) => {
      const employeeId = (newAttendance as Attendance & { employee_id?: string }).employee_id ?? newAttendance.employeeId;
      queryClient.invalidateQueries({ queryKey: attendanceKeys.lists() });
      queryClient.invalidateQueries({ queryKey: attendanceKeys.employee(employeeId) });
      queryClient.invalidateQueries({ queryKey: [...attendanceKeys.all, 'date', newAttendance.date] });
      queryClient.invalidateQueries({ queryKey: [...attendanceKeys.all, 'summary', employeeId] });
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
    mutationFn: async (data: AttendanceCreateDTO[]) => {
      const res = await apiClient.post<Attendance[]>(`${ATTENDANCE_ENDPOINT}/bulk`, data);
      return res.data;
    },
    onSuccess: () => {
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
    mutationFn: async ({ id, data }: { id: string; data: AttendanceUpdateDTO }) => {
      const res = await apiClient.patch<Attendance>(`${ATTENDANCE_ENDPOINT}/${id}`, data);
      return res.data;
    },
    onSuccess: (updatedAttendance: Attendance) => {
      queryClient.setQueryData(
        attendanceKeys.detail(updatedAttendance.id),
        updatedAttendance
      );
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
    mutationFn: async (id: string) => {
      const res = await apiClient.delete<{ success: boolean; message: string }>(
        `${ATTENDANCE_ENDPOINT}/${id}`
      );
      return res.data;
    },
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: attendanceKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: attendanceKeys.lists() });
      handleApiSuccess('Attendance deleted successfully!');
    },
    onError: (error) => {
      handleApiError(error);
    },
  });
};
