import { Employee } from "@/types/employee";
import { Attendance } from "@/types/attendance";
import { getAttendanceColor, getAttendanceIcon, formatDate } from "@/utils/attendanceUtils";

export const AttendanceCell = ({ employee }: { employee?: Employee }) => {
  if (!employee) {
    return (
      <div className="text-gray-500 dark:text-gray-400">
        Employee data not available
      </div>
    );
  }

  return (
    <div className="flex items-center gap-4">
      <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center dark:bg-gray-600">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
          {employee.full_name?.split(" ").map(n => n[0]).join("") || 'N/A'}
        </span>
      </div>
      <div>
        <div className="font-medium text-gray-900 dark:text-gray-100">{employee.full_name || 'N/A'}</div>
        <div className="text-gray-500 text-sm dark:text-gray-400">{employee.email || 'N/A'}</div>
      </div>
    </div>
  );
};

export const StatusBadge = ({ status }: { status: Attendance["status"] | string }) => {
  const s = (status || '').toLowerCase();
  const label = s === 'na' || s === 'n/a' || s === ''
    ? 'N/A'
    : status!.charAt(0).toUpperCase() + status!.slice(1).replace('-', ' ');
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getAttendanceColor(status)}`}>
      <span aria-hidden>{getAttendanceIcon(status)}</span>
      {label}
    </span>
  );
};

export const DateCell = ({ date }: { date: string }) => (
  <div className="text-sm text-gray-900 dark:text-gray-100">
    {formatDate(date)}
  </div>
);
