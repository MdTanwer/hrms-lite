import { ChevronDownIcon } from "@/icons";

interface DepartmentSelectProps {
  selectedDepartment: string;
  onDepartmentChange: (value: string) => void;
  departments: string[];
  className?: string;
}

const DepartmentSelect: React.FC<DepartmentSelectProps> = ({
  selectedDepartment,
  onDepartmentChange,
  departments,
  className = "",
}) => {
  return (
    <div className={`relative w-full ${className}`.trim()}>
      <select
        value={selectedDepartment}
        onChange={(e) => onDepartmentChange(e.target.value)}
        className="w-full min-w-0 cursor-pointer appearance-none rounded-md border border-gray-300 bg-white py-2 pl-3 pr-10 text-sm text-gray-900 transition-colors focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400"
        aria-label="Filter by department"
      >
        <option value="all">All departments</option>
        {departments.map((dept) => (
          <option key={dept} value={dept}>
            {dept}
          </option>
        ))}
      </select>
      <div
        className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 dark:text-gray-500"
        aria-hidden
      >
        <ChevronDownIcon className="h-4 w-4 shrink-0" />
      </div>
    </div>
  );
};

export default DepartmentSelect;
