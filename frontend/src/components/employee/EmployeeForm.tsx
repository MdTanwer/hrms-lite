import { FormikProps } from "formik";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import type { EmployeeFormValues } from "@/schemas/employeeSchema";

const DEPARTMENT_OPTIONS = [
  { value: "Engineering", label: "Engineering" },
  { value: "HR", label: "HR" },
  { value: "Sales", label: "Sales" },
  { value: "Marketing", label: "Marketing" },
  { value: "Finance", label: "Finance" },
] as const;

export interface EmployeeFormProps {
  formik: FormikProps<EmployeeFormValues>;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export default function EmployeeForm({
  formik,
  onSubmit,
  onCancel,
  isLoading = false,
}: EmployeeFormProps) {
  const { values, errors, touched, setFieldValue, setFieldTouched, resetForm } = formik;

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input
          label="Employee ID"
          name="employeeId"
          value={values.employeeId}
          onChange={(e) => setFieldValue("employeeId", e.target.value)}
          onBlur={() => setFieldTouched("employeeId")}
          error={touched.employeeId ? errors.employeeId : undefined}
          placeholder="EMP001"
          required
        />
        <Input
          label="Full Name"
          name="fullName"
          value={values.fullName}
          onChange={(e) => setFieldValue("fullName", e.target.value)}
          onBlur={() => setFieldTouched("fullName")}
          error={touched.fullName ? errors.fullName : undefined}
          placeholder="John Doe"
          required
        />
      </div>

      <Input
        label="Email Address"
        name="email"
        type="email"
        value={values.email}
        onChange={(e) => setFieldValue("email", e.target.value)}
        onBlur={() => setFieldTouched("email")}
        error={touched.email ? errors.email : undefined}
        placeholder="john.doe@company.com"
        required
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Select
          label="Department"
          name="department"
          value={values.department}
          onChange={(e) => setFieldValue("department", e.target.value)}
          onBlur={() => setFieldTouched("department")}
          error={touched.department ? errors.department : undefined}
          options={[...DEPARTMENT_OPTIONS]}
          required
          className="dark:bg-gray-700 dark:border-gray-600"
        />
        <Input
          label="Position"
          name="position"
          value={values.position ?? ""}
          onChange={(e) => setFieldValue("position", e.target.value)}
          onBlur={() => setFieldTouched("position")}
          error={touched.position ? errors.position : undefined}
          placeholder="Software Engineer"
        />
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-600">
        <Button
          type="button"
          variant="outline"
          onClick={() => {
            resetForm();
            onCancel();
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
          {isLoading ? "Adding Employee…" : "Add Employee"}
        </Button>
      </div>
    </form>
  );
}
