import { useState, useEffect } from 'react';
import { Employee } from '../types/employee';
import { Attendance } from '../types/attendance';

// Mock data
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
  },
  {
    employeeId: 'EMP004',
    fullName: 'Sarah Wilson',
    email: 'sarah.wilson@company.com',
    department: 'Engineering',
    position: 'Frontend Developer',
    salary: 70000,
    startDate: '2022-08-20',
    status: 'active'
  },
  {
    employeeId: 'EMP005',
    fullName: 'Tom Brown',
    email: 'tom.brown@company.com',
    department: 'Marketing',
    position: 'Marketing Manager',
    salary: 68000,
    startDate: '2021-11-15',
    status: 'active'
  }
];

const mockAttendances: Attendance[] = [
  { id: '1', employeeId: 'EMP001', date: '2024-01-15', status: 'present', markedBy: 'Admin', markedAt: '2024-01-15T09:00:00Z' },
  { id: '2', employeeId: 'EMP002', date: '2024-01-15', status: 'present', markedBy: 'Admin', markedAt: '2024-01-15T09:05:00Z' },
  { id: '3', employeeId: 'EMP003', date: '2024-01-15', status: 'absent', markedBy: 'Admin', markedAt: '2024-01-15T10:00:00Z' },
  { id: '4', employeeId: 'EMP004', date: '2024-01-15', status: 'present', markedBy: 'Admin', markedAt: '2024-01-15T09:00:00Z' },
  { id: '5', employeeId: 'EMP005', date: '2024-01-15', status: 'present', markedBy: 'Admin', markedAt: '2024-01-15T09:02:00Z' },
  { id: '6', employeeId: 'EMP001', date: '2024-01-14', status: 'present', markedBy: 'Admin', markedAt: '2024-01-14T09:00:00Z' },
  { id: '7', employeeId: 'EMP002', date: '2024-01-14', status: 'present', markedBy: 'Admin', markedAt: '2024-01-14T09:00:00Z' },
  { id: '8', employeeId: 'EMP003', date: '2024-01-14', status: 'present', markedBy: 'Admin', markedAt: '2024-01-14T09:00:00Z' },
  { id: '9', employeeId: 'EMP004', date: '2024-01-14', status: 'present', markedBy: 'Admin', markedAt: '2024-01-14T08:55:00Z' },
  { id: '10', employeeId: 'EMP005', date: '2024-01-14', status: 'present', markedBy: 'Admin', markedAt: '2024-01-14T09:01:00Z' }
];

export const useDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [employees] = useState<Employee[]>(mockEmployees);
  const [attendances] = useState<Attendance[]>(mockAttendances);

  useEffect(() => {
    // Simulate API call
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  const getDashboardStats = () => {
    const totalEmployees = employees.length;
    const activeEmployees = employees.filter(emp => emp.status === 'active').length;
    const totalDepartments = new Set(employees.map(emp => emp.department)).size;
    
    // Calculate attendance stats
    const todayAttendances = attendances.filter(att => att.date === '2024-01-15');
    const presentToday = todayAttendances.filter(att => att.status === 'present').length;
    const absentToday = todayAttendances.filter(att => att.status === 'absent').length;
    
    const attendanceRate = todayAttendances.length > 0 
      ? Math.round((presentToday / todayAttendances.length) * 100) 
      : 0;

    // Department breakdown
    const departmentStats = employees.reduce((acc, emp) => {
      acc[emp.department] = (acc[emp.department] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Recent activities (last 5 attendances)
    const recentActivities = attendances
      .sort((a, b) => new Date(b.markedAt).getTime() - new Date(a.markedAt).getTime())
      .slice(0, 5)
      .map(att => {
        const employee = employees.find(emp => emp.employeeId === att.employeeId);
        return {
          ...att,
          employeeName: employee?.fullName || 'Unknown',
          employeeDepartment: employee?.department || 'Unknown'
        };
      });

    return {
      totalEmployees,
      activeEmployees,
      totalDepartments,
      presentToday,
      absentToday,
      attendanceRate,
      departmentStats,
      recentActivities
    };
  };

  return {
    loading,
    employees,
    attendances,
    getDashboardStats
  };
};
