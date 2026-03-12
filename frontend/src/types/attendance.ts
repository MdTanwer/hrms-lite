/** Backend returns snake_case; we accept both for compatibility */
export interface Attendance {
  id: string;
  employee_id?: string;
  employeeId?: string;
  date: string;
  status: 'present' | 'absent' | 'half-day' | 'leave';
  marked_by?: string;
  markedBy?: string;
  marked_at?: string;
  markedAt?: string;
  notes?: string;
}

/** Wrapper for POST /attendance response */
export interface AttendanceApiResponse {
  success: boolean;
  message: string;
  data: Attendance;
  timestamp?: string;
}

export interface AttendanceRecord {
  employee: any;
  attendances: Attendance[];
  presentDays: number;
  absentDays: number;
  lateDays: number;
  halfDays: number;
}

/** Request body for POST /attendance (mark attendance) */
export interface AttendanceCreateDTO {
  employee_id: string;
  date: string;
  status: 'present' | 'absent' | 'half-day' | 'leave';
  notes?: string;
  marked_by?: string;
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

/** GET /attendance/employee/{employee_id}/stats?start_date=&end_date= */
export interface EmployeeAttendanceStats {
  total_days: number;
  present_days: number;
  absent_days: number;
  half_days: number;
  leave_days: number;
  attendance_rate: number;
}

export interface EmployeeAttendanceStatsApiResponse {
  success: boolean;
  message: string;
  data: EmployeeAttendanceStats;
  timestamp?: string;
}
