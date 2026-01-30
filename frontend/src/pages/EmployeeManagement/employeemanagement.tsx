import { useState } from 'react';
import PageMeta from "../../components/common/PageMeta";
import PageBreadCrumb from "../../components/common/PageBreadCrumb";
import Button from "../../components/ui/Button";
import EmployeeSearchFilter from "../../components/employee/EmployeeSearchFilter";
import EmployeeForm from "../../components/employee/EmployeeForm";
import Modal from "../../components/Modal/Modal";
import { DataTable } from "../../components/table/DataTable";
import { EmployeeCell, StatusBadge } from "../../components/employee/EmployeeRow";
import { useZodForm } from "../../utils/validators";
import { employeeSchema } from "../../schemas/employeeSchema";
import { Employee } from '../../types/employee';

const mockEmployees: Employee[] = [
  {
    employeeId: 'EMP001',
    fullName: 'John Doe',
    email: 'john.doe@company.com',
    department: 'Engineering',
    position: 'Senior Developer',
    salary: 75000,
    startDate: '2022-01-15',
    status: 'active'
  },
  {
    employeeId: 'EMP002',
    fullName: 'Jane Smith',
    email: 'jane.smith@company.com',
    department: 'HR',
    position: 'HR Manager',
    salary: 65000,
    startDate: '2021-06-01',
    status: 'active'
  },
  {
    employeeId: 'EMP003',
    fullName: 'Mike Johnson',
    email: 'mike.johnson@company.com',
    department: 'Sales',
    position: 'Sales Representative',
    salary: 55000,
    startDate: '2023-03-10',
    status: 'on-leave'
  }
];

export default function EmployeeManagement() {
  const [employees, setEmployees] = useState<Employee[]>(mockEmployees);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('all');

  const form = useZodForm(employeeSchema, {
    fullName: '',
    employeeId: '',
    email: '',
    department: '',
    position: '',
    salary: 0,
    startDate: '',
    status: 'active'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (form.validateForm()) {
      // Add employee logic here
      console.log('Form submitted:', form.values);
      setIsModalOpen(false);
      form.resetForm();
    }
  };

  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = employee.fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDepartment = selectedDepartment === 'all' || employee.department === selectedDepartment;
    return matchesSearch && matchesDepartment;
  });

  const departments = Array.from(new Set(employees.map(emp => emp.department)));

  const columns = [
    {
      key: "employee",
      header: "Employee",
      render: (emp: Employee) => <EmployeeCell {...emp} />
    },
    {
      key: "department",
      header: "Department"
    },
    {
      key: "position",
      header: "Position"
    },
    {
      key: "status",
      header: "Status",
      render: (emp: Employee) => <StatusBadge status={emp.status} />
    },
    {
      key: "actions",
      header: "Actions",
      render: () => (
        <>
          <button className="text-blue-600 hover:text-blue-800 mr-3 dark:text-blue-400 dark:hover:text-blue-300">Edit</button>
          <button className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">Delete</button>
        </>
      )
    }
  ];

  return (
    <>
      <PageMeta
        title="Employee Managemedfvdsfdsfsdnt | HRMS Lite"
        description="Manage employees, view details, and handle HR operations"
      />
         <PageBreadCrumb pageTitle="Employee Management" />
      <div className="grid grid-cols-12 gap-4 md:gap-6">
        
        <div className="col-span-12">
          <div className="rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800 dark:shadow-gray-900/10">
            <div className="border-b border-gray-200 p-6 dark:border-gray-700">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">Employee Directory</h2>
                <Button onClick={() => setIsModalOpen(true)}>
                  Add Employee
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
              data={filteredEmployees}
              emptyMessage="No employees found"
            />
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
        />
      </Modal>
    </>
  );
}
