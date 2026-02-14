import { useMemo, useState } from 'react';
import { Employee } from '@/types/employee';
import { DataTable } from '@/components/table/DataTable';
import Select from '@/components/ui/Select';
import { useEmployeeAttendance, useEmployeeAttendanceStats } from '@/hooks/queries/useAttendance';
import { StatusBadge } from '@/components/attendance/AttendanceRow';
import AttendanceDetailsStats from '@/components/attendance/AttendanceDetailsStats';
import { formatDate, getAttendanceRowClass } from '@/utils/attendanceUtils';

/** GET /attendance defaults: skip=0, limit=100; one month needs at most 31 */
const ATTENDANCE_PAGE_SIZE = 100;

const MONTHS = [
  { value: '1', label: 'January' }, { value: '2', label: 'February' }, { value: '3', label: 'March' },
  { value: '4', label: 'April' }, { value: '5', label: 'May' }, { value: '6', label: 'June' },
  { value: '7', label: 'July' }, { value: '8', label: 'August' }, { value: '9', label: 'September' },
  { value: '10', label: 'October' }, { value: '11', label: 'November' }, { value: '12', label: 'December' },
];

function getYears() {
  const current = new Date().getFullYear();
  return Array.from({ length: 5 }, (_, i) => ({
    value: String(current - i),
    label: String(current - i),
  }));
}

function toLocalDateString(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/** Returns 1st and last day of the given month as YYYY-MM-DD (full month range for API). */
function getMonthStartEnd(year: number, month: number) {
  const start = new Date(year, month - 1, 1); // 1st of month
  const end = new Date(year, month, 0);       // last day of month
  return {
    startDate: toLocalDateString(start),
    endDate: toLocalDateString(end),
  };
}

type AttendanceRecord = {
  id?: string;
  date: string;
  status: string;
};

interface AttendanceDetailsProps {
  employee: Employee | null;
}

/** Default to current month so Feb shows 1 Feb–end Feb, March shows full March, etc. */
function getCurrentMonthYear() {
  const n = new Date();
  return { month: String(n.getMonth() + 1), year: String(n.getFullYear()) };
}

export default function AttendanceDetails({ employee }: AttendanceDetailsProps) {
  const [month, setMonth] = useState(() => getCurrentMonthYear().month);
  const [year, setYear] = useState(() => getCurrentMonthYear().year);

  const yearNum = parseInt(year, 10);
  const monthNum = parseInt(month, 10);
  const { startDate, endDate } = useMemo(
    () => getMonthStartEnd(yearNum, monthNum),
    [yearNum, monthNum]
  );
  const filterParams = useMemo(
    () => ({
      start_date: startDate,
      end_date: endDate,
      skip: 0,
      limit: ATTENDANCE_PAGE_SIZE,
    }),
    [startDate, endDate]
  );

  const employeeId = employee?.employee_id ?? (employee as { id?: string })?.id ?? '';
  const { data: attendanceResponse, isLoading } = useEmployeeAttendance(
    employeeId,
    filterParams,
    !!employeeId
  );
  const { data: statsFromApi } = useEmployeeAttendanceStats(
    employeeId,
    startDate,
    endDate,
    !!employeeId
  );

  /** Backend returns display-ready list (id, date, status); use as-is */
  const allRecords: AttendanceRecord[] = attendanceResponse?.data ?? [];

  const totalFromApi = attendanceResponse?.total ?? allRecords.length;

  const columns = [
    {
      key: 'date',
      header: 'Date',
      render: (row: AttendanceRecord) => (
        <span className="text-sm text-gray-900 dark:text-gray-100">{formatDate(row.date)}</span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      render: (row: AttendanceRecord) => <StatusBadge status={row.status} />,
    },
  ];

  if (!employee) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <img
          src="/image-denger.png"
          alt="Attendance"
          className="h-32 w-auto object-contain mb-4 opacity-90 dark:opacity-80"
        />
        <p className="text-gray-500 dark:text-gray-400">Select an employee to view attendance.</p>
      </div>
    );
  }

  const yearOptions = getYears();
  const selectedMonthLabel = MONTHS.find((m) => m.value === month)?.label ?? month;
  const periodLabel = `${selectedMonthLabel} ${year}`;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-4 items-end">
        <div className="min-w-[140px]">
          <Select
            label="Month"
            options={MONTHS}
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            fullWidth
          />
        </div>
        <div className="min-w-[120px]">
          <Select
            label="Year"
            options={yearOptions}
            value={year}
            onChange={(e) => setYear(e.target.value)}
            fullWidth
          />
        </div>
      </div>
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Showing attendance for <span className="font-medium text-gray-700 dark:text-gray-300">{periodLabel}</span>
        {totalFromApi > 0 && (
          <span className="ml-1">({totalFromApi} record{totalFromApi !== 1 ? 's' : ''})</span>
        )}
      </p>

      <AttendanceDetailsStats
        totalLeave={statsFromApi?.leave_days ?? 0}
        totalAbsent={statsFromApi?.absent_days ?? 0}
        workingDays={statsFromApi?.total_days ?? 0}
        presentDays={statsFromApi?.present_days ?? 0}
        halfDays={statsFromApi?.half_days ?? 0}
        attendanceRate={statsFromApi?.attendance_rate}
      />

      <div key={`table-${year}-${month}`}>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date-wise attendance (1 month)</h4>
        <DataTable<AttendanceRecord>
          columns={columns}
          data={allRecords}
          emptyMessage="No attendance records for this month"
          loading={isLoading}
          getRowClassName={(row) => getAttendanceRowClass(row.status || '')}
        />
      </div>
    </div>
  );
}
