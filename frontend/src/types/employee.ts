export interface Employee {
  employeeId: string;
  fullName: string;
  email: string;
  department: string;
  position: string;
  salary: number;
  startDate: string;
  status: 'active' | 'inactive' | 'on-leave';
  avatar?: string;
}

export interface EmployeeFormData {
  fullName: string;
  email: string;
  department: string;
  position: string;
  salary: number;
  startDate: string;
  status: 'active' | 'inactive' | 'on-leave';
}
