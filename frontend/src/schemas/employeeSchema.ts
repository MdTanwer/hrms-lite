import { z } from 'zod';

export const employeeSchema = z.object({
  employeeId: z
    .string()
    .min(1, 'Employee ID is required')
    .regex(/^EMP\d{1,6}$/, 'Invalid employee ID format. Must be EMP followed by 1-6 digits (e.g., EMP1, EMP001, EMP1234)')
    .transform(val => val.toUpperCase()),
  
  fullName: z
    .string()
    .min(2, 'Full name must be at least 2 characters')
    .max(100, 'Full name must be less than 100 characters'),
  
  email: z
    .string()
    .email('Invalid email address')
    .regex(/^[a-zA-Z0-9._%+-]+@(gmail\.com|yahoo\.com|outlook\.com|hotmail\.com|company\.com|org\.com|net\.com)$/, 'Invalid email format')
    .toLowerCase(),
  
  department: z
    .enum(['Engineering', 'HR', 'Sales', 'Marketing', 'Finance'], {
      message: 'Department must be one of: Engineering, HR, Sales, Marketing, Finance'
    })
});

export type EmployeeFormData = z.infer<typeof employeeSchema>;
