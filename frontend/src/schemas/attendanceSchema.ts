import { z } from 'zod';

export const attendanceSchema = z.object({
  employeeId: z.string().min(1, 'Employee is required'),
  date: z.string().min(1, 'Date is required'),
  status: z.enum(['present', 'absent']),
  notes: z.string().optional()
});

export type AttendanceFormData = z.infer<typeof attendanceSchema>;
