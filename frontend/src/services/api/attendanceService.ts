import { BaseAPIService } from './baseService';
import { PaginatedResponse } from '@/types/employee';
import apiClient from '../axios';
import { Attendance } from '@/types/attendance';

export interface AttendanceCreateDTO {
  employee_id: string;
  date: string;  // YYYY-MM-DD format
  status: 'present' | 'absent' | 'half-day' | 'leave';
  notes?: string;
  marked_by?: string;
}

export interface AttendanceUpdateDTO {
  status?: 'present' | 'absent' | 'half-day' | 'leave';
  notes?: string;
}

export interface AttendanceFilterParams {
  skip?: number;
  limit?: number;
  employee_id?: string;
  start_date?: string;
  end_date?: string;
  status?: string;
  department?: string;
}

export interface AttendanceSummary {
  employee_id: string;
  employee_name?: string;
  total_days: number;
  present_days: number;
  absent_days: number;
  half_day_days: number;
  leave_days: number;
  attendance_percentage: number;
}

export interface AttendanceStats {
  total_records: number;
  present_count: number;
  absent_count: number;
  half_day_count: number;
  leave_count: number;
  attendance_rate: number;
  date_range?: {
    start: string;
    end: string;
  };
}

class AttendanceService extends BaseAPIService<Attendance> {
  constructor() {
    super('/api/v1/attendance');
  }

  /**
   * Get attendance records with filtering
   */
  async getAttendance(params?: AttendanceFilterParams): Promise<PaginatedResponse<Attendance>> {
    return this.getAll(params);
  }

  /**
   * Mark attendance for single employee
   */
  async markAttendance(data: AttendanceCreateDTO): Promise<Attendance> {
    return this.create(data);
  }

  /**
   * Bulk mark attendance
   */
  async bulkMarkAttendance(data: AttendanceCreateDTO[]): Promise<Attendance[]> {
    const response = await apiClient.post<Attendance[]>(
      `${this.endpoint}/bulk`,
      data
    );
    return response.data;
  }

  /**
   * Get attendance for specific employee
   */
  async getByEmployee(
    employeeId: string,
    params?: { skip?: number; limit?: number; start_date?: string; end_date?: string }
  ): Promise<PaginatedResponse<Attendance>> {
    const response = await apiClient.get<PaginatedResponse<Attendance>>(
      `${this.endpoint}/employee/${employeeId}`,
      { params }
    );
    return response.data;
  }

  /**
   * Get attendance for specific date
   */
  async getByDate(date: string): Promise<PaginatedResponse<Attendance>> {
    const response = await apiClient.get<PaginatedResponse<Attendance>>(
      `${this.endpoint}/date/${date}` 
    );
    return response.data;
  }

  /**
   * Update attendance record
   */
  async updateAttendance(id: string, data: AttendanceUpdateDTO): Promise<Attendance> {
    return this.patch(id, data);
  }

  /**
   * Delete attendance record
   */
  async deleteAttendance(id: string): Promise<{ success: boolean; message: string }> {
    return this.delete(id);
  }

  /**
   * Get employee attendance summary
   */
  async getEmployeeSummary(
    employeeId: string,
    params?: { start_date?: string; end_date?: string }
  ): Promise<AttendanceSummary> {
    const response = await apiClient.get<AttendanceSummary>(
      `${this.endpoint}/employee/${employeeId}/summary`,
      { params }
    );
    return response.data;
  }

  /**
   * Get attendance statistics for a date
   */
  async getStatsByDate(date: string): Promise<AttendanceStats> {
    const response = await apiClient.get<AttendanceStats>(
      `${this.endpoint}/stats/date/${date}` 
    );
    return response.data;
  }

  /**
   * Get attendance statistics for date range
   */
  async getStatsByRange(startDate: string, endDate: string): Promise<AttendanceStats> {
    const response = await apiClient.get<AttendanceStats>(
      `${this.endpoint}/stats/range`,
      { params: { start_date: startDate, end_date: endDate } }
    );
    return response.data;
  }
}

// Export singleton instance
export const attendanceService = new AttendanceService();

// Export type
export type AttendanceServiceType = typeof attendanceService;
