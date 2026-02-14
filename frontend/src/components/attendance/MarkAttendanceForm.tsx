import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import Button from '@/components/ui/Button';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import SearchableSelect from '@/components/ui/SearchableSelect';
import { useDebouncedValue } from '@/hooks/useDebouncedValue';
import { useMarkAttendance } from '@/hooks/queries/useAttendance';
import { useEmployees } from '@/hooks/queries/useEmployees';
import { getApiErrorMessage } from '@/utils/apiErrorHandler';
import { getTodayDate } from '@/utils/attendanceUtils';

const markAttendanceSchema = z.object({
  employee_id: z.string().min(1, 'Employee is required'),
  date: z
    .string()
    .min(1, 'Date is required')
    .refine((d) => d && new Date(d) <= new Date(), 'Attendance date cannot be in the future'),
  status: z.enum(['present', 'absent', 'half-day', 'leave']),
  notes: z.string().optional(),
});

type MarkAttendanceFormData = z.infer<typeof markAttendanceSchema>;

const STATUS_OPTIONS = [
  { value: 'present', label: 'Present' },
  { value: 'absent', label: 'Absent' },
  { value: 'half-day', label: 'Half Day' },
  { value: 'leave', label: 'Leave' },
];

const EMPLOYEE_SEARCH_DEBOUNCE_MS = 300;

interface MarkAttendanceFormProps {
  onSuccess?: () => void;
}

export default function MarkAttendanceForm({ onSuccess }: MarkAttendanceFormProps = {}) {
  const markAttendance = useMarkAttendance();
  const [employeeSearchQuery, setEmployeeSearchQuery] = useState('');
  const debouncedEmployeeSearch = useDebouncedValue(employeeSearchQuery, EMPLOYEE_SEARCH_DEBOUNCE_MS);

  const { data: employeesData } = useEmployees({
    search: debouncedEmployeeSearch.trim() || undefined,
    limit: 50,
  });
  const employees = employeesData?.data ?? [];
  const employeeOptions = employees.map((emp) => ({
    value: emp.employee_id ?? emp.id ?? '',
    label: emp.full_name ? `${emp.full_name} (${emp.employee_id ?? emp.id ?? 'N/A'})` : emp.email,
  })).filter((opt) => opt.value);

  const {
    register,
    handleSubmit,
    setValue,
    setError,
    watch,
    formState: { errors },
  } = useForm<MarkAttendanceFormData>({
    resolver: zodResolver(markAttendanceSchema),
    defaultValues: {
      employee_id: '',
      date: getTodayDate(),
      status: 'present',
      notes: '',
    },
  });

  const employeeId = watch('employee_id');
  const status = watch('status');

  const onSubmit = (data: MarkAttendanceFormData) => {
    markAttendance.mutate(
      {
        employee_id: data.employee_id,
        date: data.date,
        status: data.status,
        notes: data.notes || undefined,
        marked_by: 'Admin',
      },
      {
        onSuccess: () => {
          onSuccess?.();
        },
        onError: (error) => {
          const message = getApiErrorMessage(error);
          if (message === 'Attendance date cannot be in the future') {
            setError('date', { type: 'manual', message });
          }
        },
      }
    );
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <SearchableSelect
        label="Employee"
        options={employeeOptions}
        placeholder="Select employee"
        value={employeeId}
        onChange={(val) => setValue('employee_id', val, { shouldValidate: true })}
        required
        error={!!errors.employee_id}
        searchPlaceholder="Search by name or ID..."
        filterLocally={false}
        searchQuery={employeeSearchQuery}
        onSearchChange={setEmployeeSearchQuery}
      />
    

      <Input
        label="Date"
        type="date"
        required
        {...register('date')}
        error={errors.date?.message}
      />

      <Select
        label="Status"
        options={STATUS_OPTIONS}
        value={status}
        onChange={(e) => setValue('status', e.target.value as MarkAttendanceFormData['status'])}
        required
      />

      <div className="w-full">
        <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
          Notes (optional)
        </label>
        <textarea
          rows={3}
          placeholder="Optional notes"
          className="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-500 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed hover:border-gray-400 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 dark:placeholder-gray-400 dark:hover:border-gray-500 resize-y min-h-[80px]"
          {...register('notes')}
        />
      </div>

      <Button
        type="submit"
        fullWidth
        loading={markAttendance.isPending}
        disabled={markAttendance.isPending}
      >
        {markAttendance.isPending ? 'Marking...' : 'Mark Attendance'}
      </Button>
    </form>
  );
}
