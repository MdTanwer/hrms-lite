import { FormikValues } from 'formik';
import Button from '../ui/Button';
import Input from '../ui/Input';
import Select from '../ui/Select';

interface EmployeeFormProps {
  form: FormikValues;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  setIsModalOpen: (open: boolean) => void;
  isLoading?: boolean;
}

const EmployeeForm: React.FC<EmployeeFormProps> = ({
  form,
  handleSubmit,
  setIsModalOpen,
  isLoading = false,
}) => {
  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="Employee ID"
          value={form.values.employeeId || ''}
          onChange={(e) => form.setFieldValue('employeeId', e.target.value)}
          onBlur={() => form.setFieldTouched('employeeId')}
          error={form.errors.employeeId}
          placeholder="EMP001"
          required
          className="dark:bg-gray-700 dark:border-gray-600"
        />
        <Input
          label="Full Name"
          value={form.values.fullName || ''}
          onChange={(e) => form.setFieldValue('fullName', e.target.value)}
          onBlur={() => form.setFieldTouched('fullName')}
          error={form.errors.fullName}
          placeholder="John Doe"
          required
          className="dark:bg-gray-700 dark:border-gray-600"
        />
      </div>
      
      <Input
        label="Email Address"
        type="email"
        value={form.values.email || ''}
        onChange={(e) => form.setFieldValue('email', e.target.value)}
        onBlur={() => form.setFieldTouched('email')}
        error={form.errors.email}
        placeholder="john.doe@company.com"
        required
        className="dark:bg-gray-700 dark:border-gray-600"
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
          required
          className="dark:bg-gray-700 dark:border-gray-600"
        />
        <Input
          label="Position"
          value={form.values.position || ''}
          onChange={(e) => form.setFieldValue('position', e.target.value)}
          onBlur={() => form.setFieldTouched('position')}
          error={form.errors.position}
          placeholder="Software Engineer"
          required
          className="dark:bg-gray-700 dark:border-gray-600"
        />
      </div>
      
      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-600">
        <Button
          variant="outline"
          type="button"
          onClick={() => {
            setIsModalOpen(false);
            form.resetForm();
          }}
          className="dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        >
          Cancel
        </Button>
        <Button 
          type="submit"
          disabled={isLoading}
          className="dark:bg-blue-600 dark:hover:bg-blue-700"
        >
          {isLoading ? 'Adding Employee...' : 'Add Employee'}
        </Button>
      </div>
    </form>
  );
};

export default EmployeeForm;
