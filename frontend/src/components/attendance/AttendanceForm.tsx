import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { attendanceSchema, AttendanceFormData } from '../../schemas/attendanceSchema';
import { Employee } from '../../types/employee';
import Button from '../ui/Button';
import Input from '../ui/Input';
import Select from '../ui/Select';

interface AttendanceFormProps {
  onSubmit: (data: AttendanceFormData) => void;
  onCancel: () => void;
  employees: Employee[];
}

const AttendanceForm: React.FC<AttendanceFormProps> = ({
  onSubmit,
  onCancel,
  employees
}) => {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<AttendanceFormData>({
    resolver: zodResolver(attendanceSchema),
    defaultValues: {
      date: new Date().toISOString().split('T')[0],
      status: 'present',
      notes: ''
    }
  });

  const onFormSubmit = (data: AttendanceFormData) => {
    onSubmit(data);
    reset();
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 gap-4">
        <Select
          label="Employee"
          {...register('employeeId')}
          error={errors.employeeId?.message}
          options={employees.map(emp => ({
            value: emp.employee_id,
            label: `${emp.full_name} (${emp.employee_id})`
          }))}
        />
        
        <Input
          label="Date"
          type="date"
          {...register('date')}
          error={errors.date?.message}
        />
        
        <Select
          label="Status"
          {...register('status')}
          error={errors.status?.message}
          options={[
            { value: 'present', label: 'Present' },
            { value: 'absent', label: 'Absent' }
          ]}
        />
        
        <Input
          label="Notes (Optional)"
          {...register('notes')}
          error={errors.notes?.message}
          placeholder="Additional notes..."
        />
      </div>
      
      <div className="flex justify-end gap-3 pt-4">
        <Button
          variant="outline"
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Marking...' : 'Mark Attendance'}
        </Button>
      </div>
    </form>
  );
};

export default AttendanceForm;
