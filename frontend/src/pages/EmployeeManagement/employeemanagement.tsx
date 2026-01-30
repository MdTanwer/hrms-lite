import { useState, useEffect } from 'react';
import PageMeta from "../../components/common/PageMeta";
import PageBreadCrumb from "../../components/common/PageBreadCrumb";
import Button from "../../components/ui/Button";
import EmployeeSearchFilter from "../../components/employee/EmployeeSearchFilter";
import EmployeeForm from "../../components/employee/EmployeeForm";
import Modal from "../../components/Modal/Modal";
import ConfirmModal from "../../components/ui/ConfirmModal";
import { DataTable } from "../../components/table/DataTable";
import { useZodForm } from "../../utils/validators";
import { employeeSchema } from "../../schemas/employeeSchema";
import { Employee } from '../../types/employee';
import { useEmployees, useCreateEmployee, useDeleteEmployee } from '../../hooks/queries/useEmployees';
import { handleApiError } from '../../utils/apiErrorHandler';
import toast from 'react-hot-toast';
import Pagination from '../../components/ui/Pagination';

export default function EmployeeManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [employeeToDelete, setEmployeeToDelete] = useState<Employee | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  // Debounce search term - wait 500ms after user stops typing
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Fetch employees from API - backend handles all filtering
  const { data: employeesData, isLoading, error } = useEmployees({ 
    search: debouncedSearchTerm.length >= 3 ? debouncedSearchTerm : undefined,
    department: selectedDepartment === 'all' ? undefined : selectedDepartment,
    skip: currentPage * pageSize,
    limit: pageSize
  });
  const employees = employeesData?.data || [];
  const totalItems = employeesData?.total || 0;
  const totalPages = employeesData?.total_pages || 0;

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(0);
  }, [debouncedSearchTerm, selectedDepartment, pageSize]);

  const form = useZodForm(employeeSchema, {
    employeeId: '',
    fullName: '',
    email: '',
    department: 'Engineering',
  });

  // Create employee mutation
  const createEmployeeMutation = useCreateEmployee(() => {
    // Success callback - close modal and reset form
    setIsModalOpen(false);
    form.resetForm();
  });

  // Delete employee mutation
  const deleteEmployeeMutation = useDeleteEmployee();

  // Handle delete employee
  const handleDeleteEmployee = (employee: Employee) => {
    setEmployeeToDelete(employee);
    setDeleteModalOpen(true);
  };

  // Confirm delete employee
  const confirmDeleteEmployee = () => {
    if (employeeToDelete && employeeToDelete.employee_id) {
      deleteEmployeeMutation.mutate(employeeToDelete.employee_id);
      setDeleteModalOpen(false);
      setEmployeeToDelete(null);
    }
  };

  // Cancel delete
  const cancelDeleteEmployee = () => {
    setDeleteModalOpen(false);
    setEmployeeToDelete(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const isValid = form.validateForm();
    if (!isValid) {
      // Show validation errors to user
      if (form.errors && Object.keys(form.errors).length > 0) {
        const firstError = Object.values(form.errors)[0];
        toast.error(firstError as string);
      }
      return;
    }
    
    // Use mutate instead of mutateAsync to avoid double error handling
    createEmployeeMutation.mutate(form.values as Employee);
  };

  // Hardcoded departments from backend enum
  const departments = ['Engineering', 'HR', 'Sales', 'Marketing', 'Finance'];

  const columns = [
    {
      key: "employeeId",
      header: "Employee ID",
      render: (emp: Employee) => emp.employee_id
    },
    {
      key: "fullName",
      header: "Name",
      render: (emp: Employee) =>  emp.full_name
    },
    {
      key: "email", 
      header: "Email",
      render: (emp: Employee) => emp.email
    },
    {
      key: "department",
      header: "Department",
      render: (emp: Employee) => emp.department
    },
    {
      key: "actions",
      header: "Actions",
      render: (emp: Employee) => (
        <div className="flex gap-2">
          <button 
            className="text-red-600 hover:text-red-800 hover:bg-red-50 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-900/20 p-2 rounded-md border border-transparent hover:border-red-200 dark:hover:border-red-800 transition-all duration-200"
            title="Delete"
            onClick={() => handleDeleteEmployee(emp)}
            disabled={deleteEmployeeMutation.isPending}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14zM10 11v6M14 11v6" />
            </svg>
          </button>
        </div>
      )
    }
  ];

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4 dark:bg-red-900/20 dark:border-red-800">
          <h3 className="text-red-800 font-medium dark:text-red-400">Error loading employees</h3>
          <p className="text-red-600 mt-1 dark:text-red-300">{handleApiError(error)}</p>
        </div>
      </div>
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
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">Employee Directory</h2>
                <Button 
                  onClick={() => setIsModalOpen(true)}
                  disabled={isLoading}
                >
                  {isLoading ? 'Loading...' : 'Add Employee'}
                </Button>
              </div>
              
              <EmployeeSearchFilter
                searchTerm={searchTerm}
                onSearchChange={setSearchTerm}
                selectedDepartment={selectedDepartment}
                onDepartmentChange={setSelectedDepartment}
                departments={departments}
              />
            </div>
            
            <DataTable
              columns={columns}
              data={employees}
              emptyMessage={isLoading ? "Loading employees..." : "No employees found"}
              loading={isLoading}
            />
            
            {/* Pagination */}
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
                  showPageSizeSelector={true}
                  showInfo={true}
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
          form.resetForm();
        }}
        title="Add New Employee"
        size="lg"
      >
        <EmployeeForm
          form={form}
          handleSubmit={handleSubmit}
          setIsModalOpen={setIsModalOpen}
          isLoading={createEmployeeMutation.isPending}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
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
          employeeToDelete && (
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <div className="space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100 min-w-0">Employee:</span>
                  <span className="text-sm text-gray-600 dark:text-gray-300 break-words">
                    {employeeToDelete.full_name} ({employeeToDelete.employee_id})
                  </span>
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                  <span className="text-sm font-medium text-gray-900 dark:text-gray-100 min-w-0">Email:</span>
                  <span className="text-sm text-gray-600 dark:text-gray-300 break-words">{employeeToDelete.email}</span>
                </div>
              </div>
            </div>
          )
        }
      />
    </>
  );
}
