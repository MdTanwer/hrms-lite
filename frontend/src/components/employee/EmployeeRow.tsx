import { Employee } from "@/types/employee";

export const EmployeeCell = (employee: Employee) => (
  <div className="flex items-center gap-4">
    <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center dark:bg-gray-600">
      <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
        {employee?.full_name?.split(" ").map(n => n[0]).join("") || "U"}
      </span>
    </div>
    <div>
      <div className="font-medium text-gray-900 dark:text-gray-100">{employee?.full_name || "Unknown"}</div>
      <div className="text-gray-500 text-sm dark:text-gray-400">{employee?.email || "No email"}</div>
    </div>
  </div>
);
