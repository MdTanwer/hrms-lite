import { useState, useEffect } from "react";
import { useFormik } from "formik";
import toast from "react-hot-toast";

import PageMeta from "@/components/common/PageMeta";
import PageBreadCrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/Button";
import EmployeeSearch from "@/components/employee/EmployeeSearch";
import DepartmentSelect from "@/components/ui/DepartmentSelect";
import EmployeeForm from "@/components/employee/EmployeeForm";
import Modal from "@/components/Modal/Modal";
import ConfirmModal from "@/components/ui/ConfirmModal";
import { DataTable } from "@/components/table/DataTable";
import Pagination from "@/components/ui/Pagination";

import {
  defaultEmployeeFormValues,
  employeeSchema,
  type EmployeeFormValues,
} from "@/schemas/employeeSchema";
import { validateWithZod } from "@/utils/validators";
import { Employee } from "@/types/employee";
import {
  useEmployees,
  useCreateEmployee,
  useDeleteEmployee,
} from "@/hooks/queries/useEmployees";
import ErrorState from "@/components/common/ErrorState";
import { TrashIcon } from "@/icons";

const DEPARTMENTS = ["Engineering", "HR", "Sales", "Marketing", "Finance"] as const;

export default function EmployeeManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [employeeToDelete, setEmployeeToDelete] = useState<Employee | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDepartment, setSelectedDepartment] = useState<string>("all");
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearchTerm(searchTerm), 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const { data: employeesData, isLoading, error, refetch } = useEmployees({
    search: debouncedSearchTerm.length >= 3 ? debouncedSearchTerm : undefined,
    department: selectedDepartment === "all" ? undefined : selectedDepartment,
    skip: currentPage * pageSize,
    limit: pageSize,
  });

  const employees = employeesData?.data ?? [];
  const totalItems = employeesData?.total ?? 0;
  const totalPages = employeesData?.total_pages ?? 0;

  useEffect(() => {
    setCurrentPage(0);
  }, [debouncedSearchTerm, selectedDepartment, pageSize]);

  const formik = useFormik<EmployeeFormValues>({
    initialValues: defaultEmployeeFormValues,
    validate: (values) => validateWithZod(employeeSchema, values),
    onSubmit: () => {}, // Handled in handleSubmit so we can use mutation
  });

  const createEmployeeMutation = useCreateEmployee(() => {
    setIsModalOpen(false);
    formik.resetForm({ values: defaultEmployeeFormValues });
  });

  const deleteEmployeeMutation = useDeleteEmployee();

  const handleDeleteEmployee = (employee: Employee) => {
    setEmployeeToDelete(employee);
    setDeleteModalOpen(true);
  };

  const confirmDeleteEmployee = () => {
    const id = employeeToDelete?.employee_id;
    if (!id) return;
    deleteEmployeeMutation.mutate(id);
    setDeleteModalOpen(false);
    setEmployeeToDelete(null);
  };

  const cancelDeleteEmployee = () => {
    setDeleteModalOpen(false);
    setEmployeeToDelete(null);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    formik.setTouched({
      employeeId: true,
      fullName: true,
      email: true,
      department: true,
      position: true,
    });
    const parsed = employeeSchema.safeParse(formik.values);
    if (!parsed.success) {
      const errors: Record<string, string> = {};
      parsed.error.issues.forEach((issue) => {
        const key = issue.path[0];
        if (typeof key === "string" && !(key in errors)) errors[key] = issue.message;
      });
      formik.setErrors(errors);
      const firstMessage = Object.values(errors)[0];
      if (firstMessage) toast.error(firstMessage);
      return;
    }
    const { position, ...rest } = parsed.data;
    createEmployeeMutation.mutate({
      ...rest,
      ...(position?.trim() && { position: position.trim() }),
    });
  };

  const columns = [
    {
      key: "employeeId",
      header: "Employee ID",
      render: (emp: Employee) => emp.employee_id ?? "",
    },
    {
      key: "fullName",
      header: "Name",
      render: (emp: Employee) => emp.full_name ?? "",
    },
    {
      key: "email",
      header: "Email",
      render: (emp: Employee) => emp.email ?? "",
    },
    {
      key: "department",
      header: "Department",
      render: (emp: Employee) => emp.department ?? "",
    },
    {
      key: "actions",
      header: "Actions",
      render: (emp: Employee) => (
        <div className="flex gap-2">
          <button
            type="button"
            className="text-red-600 hover:text-red-800 hover:bg-red-50 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-900/20 p-2 rounded-md border border-transparent hover:border-red-200 dark:hover:border-red-800 transition-all duration-200"
            title="Delete"
            onClick={() => handleDeleteEmployee(emp)}
            disabled={deleteEmployeeMutation.isPending}
          >
            <TrashIcon className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  if (error) {
    return (
      <ErrorState
        title="Error loading employees"
        error={error}
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <>
      <PageMeta
        title="Employee Management | HRMS Lite"
        description="Manage employees, view details, and handle HR operations"
      />
      <PageBreadCrumb pageTitle="Employee Management" />
      <div className="grid grid-cols-12 gap-4 md:gap-6">
        <div className="col-span-12">
          <div className="rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800 dark:shadow-gray-900/10">
            <div className="border-b border-gray-200 p-6 dark:border-gray-700">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">
                  Employee Directory
                </h2>
                <Button onClick={() => setIsModalOpen(true)} disabled={isLoading}>
                  {isLoading ? "Loading…" : "Add Employee"}
                </Button>
              </div>
              <br />

              <div className="flex flex-col sm:flex-row gap-4">
                <div className="w-full min-w-0 sm:w-[80%]">
                  <EmployeeSearch searchTerm={searchTerm} onSearchChange={setSearchTerm} />
                </div>
                <div className="w-full min-w-0 sm:w-[20%]">
                  <DepartmentSelect
                    selectedDepartment={selectedDepartment}
                    onDepartmentChange={setSelectedDepartment}
                    departments={[...DEPARTMENTS]}
                  />
                </div>
              </div>
            </div>

            <DataTable
              columns={columns}
              data={employees}
              emptyMessage={isLoading ? "Loading employees…" : "No employees found"}
              loading={isLoading}
            />

            {totalItems > 0 && (
              <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={setCurrentPage}
                  pageSize={pageSize}
                  onPageSizeChange={setPageSize}
                  totalItems={totalItems}
                  pageSizeOptions={[10, 25, 50, 100]}
                  showPageSizeSelector
                  showInfo
                />
              </div>
            )}
          </div>
        </div>
      </div>

      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          formik.resetForm({ values: defaultEmployeeFormValues });
        }}
        title="Add New Employee"
        size="lg"
      >
        <EmployeeForm
          formik={formik}
          onSubmit={handleSubmit}
          onCancel={() => {
            setIsModalOpen(false);
            formik.resetForm({ values: defaultEmployeeFormValues });
          }}
          isLoading={createEmployeeMutation.isPending}
        />
      </Modal>

      <ConfirmModal
        isOpen={deleteModalOpen}
        onClose={cancelDeleteEmployee}
        onConfirm={confirmDeleteEmployee}
        title="Delete Employee"
        message="Are you sure you want to delete this employee? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        variant="danger"
        isLoading={deleteEmployeeMutation.isPending}
        customContent={
          employeeToDelete ? (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <div className="space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100 min-w-0">
                    Employee:
                  </span>
                  <span className="text-sm text-gray-600 dark:text-gray-300 break-words">
                    {employeeToDelete.full_name} ({employeeToDelete.employee_id})
                  </span>
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100 min-w-0">
                    Email:
                  </span>
                  <span className="text-sm text-gray-600 dark:text-gray-300 break-words">
                    {employeeToDelete.email}
                  </span>
                </div>
              </div>
            </div>
          ) : undefined
        }
      />
    </>
  );
}
