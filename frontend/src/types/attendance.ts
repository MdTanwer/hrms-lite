export interface Attendance {
  id: string;
  employeeId: string;
  date: string; // YYYY-MM-DD format
  status: 'present' | 'absent' | 'late' | 'half-day';
  markedBy: string; // admin who marked
  markedAt: string; // timestamp
  notes?: string;
}

export interface AttendanceRecord {
  employee: any; // Employee type
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
