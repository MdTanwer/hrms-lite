import Input from '../ui/Input';
import Select from '../ui/Select';

interface AttendanceFilterProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  selectedDepartment: string;
  onDepartmentChange: (value: string) => void;
  selectedStatus: string;
  onStatusChange: (value: string) => void;
  dateRange: {
    start: string;
    end: string;
  };
  onDateRangeChange: (range: { start: string; end: string }) => void;
  departments: string[];
}

const AttendanceFilter: React.FC<AttendanceFilterProps> = ({
  searchTerm,
  onSearchChange,
  selectedDepartment,
  onDepartmentChange,
  selectedStatus,
  onStatusChange,
  dateRange,
  onDateRangeChange,
  departments
}) => {
  return (
    <div className="flex flex-col lg:flex-row gap-4">
      <div className="flex-1">
        <Input
          placeholder="Search employees..."
          value={searchTerm}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full"
        />
      </div>
      
      <Select
        value={selectedDepartment}
        onChange={(e) => onDepartmentChange(e.target.value)}
        options={[
          { value: 'all', label: 'All Departments' },
          ...departments.map(dept => ({ value: dept, label: dept }))
        ]}
        className="w-full lg:w-48"
      />
      
      <Select
        value={selectedStatus}
        onChange={(e) => onStatusChange(e.target.value)}
        options={[
          { value: 'all', label: 'All Status' },
          { value: 'present', label: 'Present' },
          { value: 'absent', label: 'Absent' },
          { value: 'late', label: 'Late' },
          { value: 'half-day', label: 'Half Day' }
        ]}
        className="w-full lg:w-48"
      />
      
      <div className="flex gap-2">
        <Input
          type="date"
          value={dateRange.start}
          onChange={(e) => onDateRangeChange({ ...dateRange, start: e.target.value })}
          className="w-full lg:w-40"
        />
        <Input
          type="date"
          value={dateRange.end}
          onChange={(e) => onDateRangeChange({ ...dateRange, end: e.target.value })}
          className="w-full lg:w-40"
        />
      </div>
    </div>
  );
};

export default AttendanceFilter;
