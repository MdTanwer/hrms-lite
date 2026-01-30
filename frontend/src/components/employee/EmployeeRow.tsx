import { Employee } from "../../types/employee";
import { getStatusColor } from "../../utils/employeeUtils";

export const EmployeeCell = (employee: Employee) => (
  <div className="flex items-center gap-4">
    <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center dark:bg-gray-600">
      <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
        {employee.fullName.split(" ").map(n => n[0]).join("")}
      </span>
    </div>
    <div>
      <div className="font-medium text-gray-900 dark:text-gray-100">{employee.fullName}</div>
      <div className="text-gray-500 text-sm dark:text-gray-400">{employee.email}</div>
    </div>
  </div>
);

export const StatusBadge = ({ status }: { status: Employee["status"] }) => (
  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(status)}`}>
    {status}
  </span>
);
