import { FormikValues } from 'formik';
import Button from '../ui/Button';
import Input from '../ui/Input';
import Select from '../ui/Select';

interface EmployeeFormProps {
  form: FormikValues;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  setIsModalOpen: (open: boolean) => void;
}

const EmployeeForm: React.FC<EmployeeFormProps> = ({
  form,
  handleSubmit,
  setIsModalOpen,
}) => {
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Full Name"
          value={form.values.fullName || ''}
          onChange={(e) => form.setFieldValue('fullName', e.target.value)}
          onBlur={() => form.setFieldTouched('fullName')}
          error={form.errors.fullName}
          placeholder="John Doe"
        />
        <Input
          label="Employee ID"
          value={form.values.employeeId || ''}
          onChange={(e) => form.setFieldValue('employeeId', e.target.value)}
          onBlur={() => form.setFieldTouched('employeeId')}
          error={form.errors.employeeId}
          placeholder="EMP001"
        />
      </div>
      
      <Input
        label="Email"
        type="email"
        value={form.values.email || ''}
        onChange={(e) => form.setFieldValue('email', e.target.value)}
        onBlur={() => form.setFieldTouched('email')}
        error={form.errors.email}
        placeholder="john.doe@company.com"
      />
      
      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Department"
          value={form.values.department || ''}
          onChange={(e) => form.setFieldValue('department', e.target.value)}
          onBlur={() => form.setFieldTouched('department')}
          error={form.errors.department}
          options={[
            { value: 'Engineering', label: 'Engineering' },
            { value: 'HR', label: 'HR' },
            { value: 'Sales', label: 'Sales' },
            { value: 'Marketing', label: 'Marketing' },
            { value: 'Finance', label: 'Finance' },
          ]}
        />
        <Input
          label="Position"
          value={form.values.position || ''}
          onChange={(e) => form.setFieldValue('position', e.target.value)}
          onBlur={() => form.setFieldTouched('position')}
          error={form.errors.position}
          placeholder="Senior Developer"
        />
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Salary"
          type="number"
          value={form.values.salary || ''}
          onChange={(e) => form.setFieldValue('salary', Number(e.target.value))}
          onBlur={() => form.setFieldTouched('salary')}
          error={form.errors.salary}
          placeholder="75000"
        />
        <Input
          label="Start Date"
          type="date"
          value={form.values.startDate || ''}
          onChange={(e) => form.setFieldValue('startDate', e.target.value)}
          onBlur={() => form.setFieldTouched('startDate')}
          error={form.errors.startDate}
        />
      </div>
      
      <Select
        label="Status"
        value={form.values.status || ''}
        onChange={(e) => form.setFieldValue('status', e.target.value)}
        onBlur={() => form.setFieldTouched('status')}
        error={form.errors.status}
        options={[
          { value: 'active', label: 'Active' },
          { value: 'inactive', label: 'Inactive' },
          { value: 'on-leave', label: 'On Leave' },
        ]}
      />
      
      <div className="flex justify-end gap-3 pt-4">
        <Button
          variant="outline"
          type="button"
          onClick={() => {
            setIsModalOpen(false);
            form.resetForm();
          }}
        >
          Cancel
        </Button>
        <Button type="submit">
          Add Employee
        </Button>
      </div>
    </form>
  );
};

export default EmployeeForm;
