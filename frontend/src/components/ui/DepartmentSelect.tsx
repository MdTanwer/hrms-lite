interface DepartmentSelectProps {
  selectedDepartment: string;
  onDepartmentChange: (value: string) => void;
  departments: string[];
}

const ChevronIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
  </svg>
);

const DepartmentSelect: React.FC<DepartmentSelectProps> = ({
  selectedDepartment,
  onDepartmentChange,
  departments
}) => {
  return (
    <div className="relative">
      <select
        value={selectedDepartment}
        onChange={(e) => onDepartmentChange(e.target.value)}
        className="appearance-none rounded-md border border-gray-300 bg-white pl-10 pr-8 py-2 text-sm text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:focus:border-blue-400 dark:focus:ring-blue-400 transition-all duration-200 cursor-pointer"
      >
        <option value="all">All</option>
        {departments.map(dept => (
          <option key={dept} value={dept}>{dept}</option>
        ))}
      </select>
      {/* Static Dropdown Arrow Icon */}
      <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none">
        <ChevronIcon className="w-4 h-4" />
      </div>
    </div>
  );
};

export default DepartmentSelect;
