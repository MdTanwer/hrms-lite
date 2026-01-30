import { z } from 'zod';

export const employeeSchema = z.object({
  fullName: z
    .string()
    .min(2, 'Full name must be at least 2 characters')
    .max(50, 'Full name must be less than 50 characters')
    .regex(/^[a-zA-Z\s]+$/, 'Full name can only contain letters and spaces'),
  
  employeeId: z
    .string()
    .min(3, 'Employee ID must be at least 3 characters')
    .max(10, 'Employee ID must be less than 10 characters')
    .regex(/^[A-Z]{2,}\d{3,}$/, 'Employee ID must be in format like EMP001'),
  
  email: z
    .string()
    .email('Invalid email address')
    .toLowerCase(),
  
  department: z
    .string()
    .min(1, 'Department is required')
    .max(30, 'Department name is too long'),
  
  position: z
    .string()
    .min(1, 'Position is required')
    .max(50, 'Position name is too long'),
  
  salary: z
    .number()
    .min(15000, 'Salary must be at least $15,000')
    .max(500000, 'Salary cannot exceed $500,000'),
  
  startDate: z
    .string()
    .min(1, 'Start date is required')
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be in YYYY-MM-DD format'),
  
  status: z
    .enum(['active', 'inactive', 'on-leave'], {
      message: 'Status must be active, inactive, or on-leave'
    })
});

export type EmployeeFormData = z.infer<typeof employeeSchema>;
