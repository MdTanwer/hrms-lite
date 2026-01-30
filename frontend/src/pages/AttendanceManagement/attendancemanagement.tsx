import { useState, useEffect } from 'react';
import PageMeta from "../../components/common/PageMeta";
import PageBreadCrumb from "../../components/common/PageBreadCrumb";
import Button from "../../components/ui/Button";
import EmployeeSearch from "../../components/employee/EmployeeSearch";
import DepartmentSelect from "../../components/ui/DepartmentSelect";
import Pagination from "../../components/ui/Pagination";
import { DataTable } from "../../components/table/DataTable";
import { useEmployees } from "../../hooks/queries/useEmployees";
import { Employee } from "../../types/employee";

export default function AttendanceManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  
  // Use the same employee data as EmployeeManagement
  const { data: employeesData, isLoading, error } = useEmployees({
    skip: currentPage * pageSize,
    limit: pageSize
  });
  const employees = employeesData?.data || [];
  const totalItems = employeesData?.total || 0;
  const totalPages = employeesData?.total_pages || 0;

  // Filter employees based on search and department (client-side filtering)
  const filteredEmployees = employees.filter(emp => {
    const matchesSearch = searchTerm === '' || 
      emp.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      emp.employee_id?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesDepartment = selectedDepartment === 'all' || emp.department === selectedDepartment;
    
    return matchesSearch && matchesDepartment;
  });

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(0);
  }, [searchTerm, selectedDepartment, pageSize]);

  const handleModalClose = () => {
    setIsModalOpen(false);
  };

  const columns = [
    {
      key: "employeeId",
      header: "Employee ID",
      render: (emp: Employee) => emp.employee_id || 'N/A'
    },
    {
      key: "fullName",
      header: "Name",
      render: (emp: Employee) => emp.full_name || 'N/A'
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
            // TODO: Navigate to employee attendance details
            console.log(`View attendance for ${emp.full_name} (${emp.employee_id})`);
          }}
        >
          View Attendance
        </Button>
      )
    }
  ];

  // Hardcoded departments from backend enum
  const departments = ['Engineering', 'HR', 'Sales', 'Marketing', 'Finance'];

  return (
    <>
      <PageMeta
        title="Employee Management | HRMS Lite"
        description="Manage employees and view details"
      />
      <PageBreadCrumb pageTitle="Employee Management" />
      
      {error && (
        <div className="mb-6">
          <div className="bg-red-50 border border-red-200 rounded-md p-4 dark:bg-red-900/20 dark:border-red-800">
            <h3 className="text-red-800 font-medium dark:text-red-400">Error loading employees</h3>
            <p className="text-red-600 mt-1 dark:text-red-300">{error.message}</p>
          </div>
        </div>
      )}
      
      <div className="grid grid-cols-12 gap-4 md:gap-6">
        <div className="col-span-12">
          <div className="rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800 dark:shadow-gray-900/10">
            <div className="border-b border-gray-200 p-6 dark:border-gray-700">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">Employee Directory</h2>
              </div>
              
              <div className="flex gap-4">
                <div className="flex-1 flex flex-col sm:flex-row gap-4">
                  <EmployeeSearch
                    searchTerm={searchTerm}
                    onSearchChange={setSearchTerm}
                  />
                  <DepartmentSelect
                    selectedDepartment={selectedDepartment}
                    onDepartmentChange={setSelectedDepartment}
                    departments={departments}
                  />
                </div>
                <div className="w-1/5 min-w-[120px]">
                  <Button 
                    onClick={() => setIsModalOpen(true)}
                    disabled={isLoading}
                    fullWidth
                  >
                    Mark Attendance
                  </Button>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <DataTable
                columns={columns}
                data={filteredEmployees}
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
    </>
  );
}
