import { useState } from 'react';
import { Attendance } from '../types/attendance';
import { Employee } from '../types/employee';

const mockEmployees: Employee[] = [
  {
    employeeId: 'EMP001',
    fullName: 'John Doe',
    email: 'john.doe@company.com',
    department: 'Engineering',
    position: 'Senior Developer',
    salary: 75000,
    startDate: '2022-01-15',
    status: 'active'
  },
  {
    employeeId: 'EMP002',
    fullName: 'Jane Smith',
    email: 'jane.smith@company.com',
    department: 'HR',
    position: 'HR Manager',
    salary: 65000,
    startDate: '2021-06-01',
    status: 'active'
  },
  {
    employeeId: 'EMP003',
    fullName: 'Mike Johnson',
    email: 'mike.johnson@company.com',
    department: 'Sales',
    position: 'Sales Representative',
    salary: 55000,
    startDate: '2023-03-10',
    status: 'on-leave'
  }
];

const mockAttendances: (Attendance & { employee: Employee })[] = [
  {
    id: '1',
    employeeId: 'EMP001',
    date: '2024-01-15',
    status: 'present',
    markedBy: 'Admin',
    markedAt: '2024-01-15T09:00:00Z',
    employee: mockEmployees[0]
  },
  {
    id: '2',
    employeeId: 'EMP002',
    date: '2024-01-15',
    status: 'late',
    markedBy: 'Admin',
    markedAt: '2024-01-15T09:30:00Z',
    employee: mockEmployees[1]
  },
  {
    id: '3',
    employeeId: 'EMP003',
    date: '2024-01-15',
    status: 'absent',
    markedBy: 'Admin',
    markedAt: '2024-01-15T10:00:00Z',
    employee: mockEmployees[2]
  }
];

export const useAttendance = () => {
  const [attendances, setAttendances] = useState<(Attendance & { employee: Employee })[]>(mockAttendances);
  const [employees] = useState<Employee[]>(mockEmployees);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addAttendance = async (data: Omit<Attendance, 'id' | 'markedBy' | 'markedAt'>) => {
    setLoading(true);
    setError(null);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const employee = employees.find(emp => emp.employeeId === data.employeeId);
      if (!employee) {
        setError('Employee not found');
        return false;
      }

      // Check for duplicate attendance
      const existingAttendance = attendances.find(
        att => att.employeeId === data.employeeId && att.date === data.date
      );
      
      if (existingAttendance) {
        setError('Attendance already marked for this employee on this date');
        return false;
      }

      const newAttendance: Attendance & { employee: Employee } = {
        ...data,
        id: Date.now().toString(),
        markedBy: 'Admin',
        markedAt: new Date().toISOString(),
        employee
      };

      setAttendances(prev => [...prev, newAttendance]);
      return true;
    } catch (err) {
      setError('Failed to mark attendance. Please try again.');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const getAttendanceStats = () => {
    const stats = {
      total: attendances.length,
      present: 0,
      absent: 0,
      late: 0,
      halfDay: 0
    };

    attendances.forEach(att => {
      switch (att.status) {
        case 'present':
          stats.present++;
          break;
        case 'absent':
          stats.absent++;
          break;
        case 'late':
          stats.late++;
          break;
        case 'half-day':
          stats.halfDay++;
          break;
      }
    });

    const attendanceRate = stats.total > 0 ? (stats.present / stats.total) * 100 : 0;

    return {
      ...stats,
      attendanceRate: Math.round(attendanceRate * 100) / 100
    };
  };

  const clearError = () => setError(null);

  return {
    attendances,
    employees,
    loading,
    error,
    addAttendance,
    getAttendanceStats,
    clearError
  };
};
