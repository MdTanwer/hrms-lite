import { PaginatedResponse } from '@/types/employee';

export interface Attendance {
  id: string;
  employeeId: string;
  date: string;
  status: 'present' | 'absent';
  markedBy: string;
  markedAt: string;
  notes?: string;
}

export interface AttendanceRecord {
  employee: any;
  attendances: Attendance[];
  presentDays: number;
  absentDays: number;
  lateDays: number;
  halfDays: number;
}

export interface AttendanceFormData {
  employeeId: string;
  date: string;
  status: 'present' | 'absent' | 'late' | 'half-day';
  notes?: string;
}

export interface AttendanceCreateDTO {
  employee_id: string;
  date: string;
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
