import { useState, useEffect } from 'react';
import PageMeta from "@/components/common/PageMeta";
import PageBreadCrumb from "@/components/common/PageBreadCrumb";
import Button from "@/components/ui/Button";
import EmployeeSearch from "@/components/employee/EmployeeSearch";
import DepartmentSelect from "@/components/ui/DepartmentSelect";
import Pagination from "@/components/ui/Pagination";
import { DataTable } from "@/components/table/DataTable";
import ErrorState from "@/components/common/ErrorState";
import Modal from "@/components/Modal/Modal";
import AttendanceDetails from "@/components/attendance/AttendanceDetails";
import MarkAttendanceForm from "@/components/attendance/MarkAttendanceForm";
import { useEmployees } from "@/hooks/queries/useEmployees";
import { Employee } from "@/types/employee";

export default function AttendanceManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [attendanceDetailsOpen, setAttendanceDetailsOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearchTerm(searchTerm), 500);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Backend filtering: pass search and department to API (no client-side filtering)
  const { data: employeesData, isLoading, error, refetch } = useEmployees({
    skip: currentPage * pageSize,
    limit: pageSize,
    search: debouncedSearchTerm.trim().length >= 3 ? debouncedSearchTerm.trim() : undefined,
    department: selectedDepartment === 'all' ? undefined : selectedDepartment,
  });
  const employees = employeesData?.data ?? [];
  const totalItems = employeesData?.total ?? 0;
  const totalPages = employeesData?.total_pages ?? 0;

  useEffect(() => {
    setCurrentPage(0);
  }, [debouncedSearchTerm, selectedDepartment, pageSize]);



  const columns = [
    {
      key: "employeeId",
      header: "Employee ID",
      render: (emp: Employee) => emp.employee_id ?? 'N/A'
    },
    {
      key: "fullName",
      header: "Name",
      render: (emp: Employee) => emp.full_name ?? 'N/A'
    },
    {
      key: "email", 
      header: "Email",
      render: (emp: Employee) => emp.email || 'N/A'
    },
    {
      key: "department",
      header: "Department",
      render: (emp: Employee) => emp.department || 'N/A'
    },
    {
      key: "status",
      header: "Status",
      render: (emp: Employee) => emp.status || 'N/A'
    },
    {
      key: "actions",
      header: "Actions",
      render: (emp: Employee) => (
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            setSelectedEmployee(emp);
            setAttendanceDetailsOpen(true);
          }}
        >
          View Attendance
        </Button>
      )
    }
  ];

  // Hardcoded departments from backend enum
  const DEPARTMENTS = ["Engineering", "HR", "Sales", "Marketing", "Finance"] as const;

  return (
    <>
      <PageMeta
        title="Employee Management | HRMS Lite"
        description="Manage employees and view details"
      />
      <PageBreadCrumb pageTitle="Employee Management" />
      
      {error && (
        <ErrorState
          title="Error loading employees"
          error={error}
          onRetry={() => refetch()}
          className="mb-6"
        />
      )}
      
      <div className="grid grid-cols-12 gap-4 md:gap-6">
        <div className="col-span-12">
          <div className="rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800 dark:shadow-gray-900/10">
            <div className="border-b border-gray-200 p-6 dark:border-gray-700">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
                <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-100 sm:text-xl order-1">
                  Employee Attendance
                </h2>
                <div className="w-full min-w-0 sm:w-auto sm:min-w-[140px] order-2">
                  <Button
                    onClick={() => setIsModalOpen(true)}
                    disabled={isLoading}
                    fullWidth
                    className="sm:w-auto"
                  >
                    Mark Attendance
                  </Button>
                </div>
              </div>
              <div className="mt-4 flex flex-col gap-4 sm:flex-row sm:gap-6">
                <div className="w-full min-w-0 sm:flex-1">
                  <EmployeeSearch searchTerm={searchTerm} onSearchChange={setSearchTerm} />
                </div>
                <div className="w-full min-w-0 sm:w-44 sm:flex-shrink-0">
                  <DepartmentSelect
                    selectedDepartment={selectedDepartment}
                    onDepartmentChange={setSelectedDepartment}
                    departments={[...DEPARTMENTS]}
                  />
                </div>
              </div>
            </div>
            
            <div className="p-6">
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
      </div>

      <Modal
        isOpen={attendanceDetailsOpen}
        onClose={() => {
          setAttendanceDetailsOpen(false);
          setSelectedEmployee(null);
        }}
        title={selectedEmployee ? `Attendance - ${selectedEmployee.full_name}` : "Attendance"}
        size="xl"
      >
        <AttendanceDetails employee={selectedEmployee} />
      </Modal>

      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Mark Attendance"
        size="md"
      >
        {isModalOpen && (
          <MarkAttendanceForm onSuccess={() => setIsModalOpen(false)} />
        )}
      </Modal>
    </>
  );
}
