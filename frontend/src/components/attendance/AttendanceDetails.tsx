import { useMemo, useState } from 'react';
import { Employee } from '@/types/employee';
import { DataTable } from '@/components/table/DataTable';
import Select from '@/components/ui/Select';
import { useEmployeeAttendance, useEmployeeAttendanceStats } from '@/hooks/queries/useAttendance';
import { StatusBadge } from '@/components/attendance/AttendanceRow';
import AttendanceDetailsStats from '@/components/attendance/AttendanceDetailsStats';
import { ATTENDANCE_PAGE_SIZE, MONTHS } from '@/constants/attendance';
import {
  formatDateShort,
  getDayOfWeek,
  getDaysInMonth,
  getMonthStartEnd,
  getYears,
  toDateKey,
} from '@/utils/attendanceUtils';

/** One row in the monthly attendance table (from API or placeholder with status N/A). */
type AttendanceTableRow = {
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

  /** Backend returns display-ready list (id, date, status) */
  const apiRecords: AttendanceTableRow[] = attendanceResponse?.data ?? [];

  /** Full month grid: one row per calendar day; missing days show status N/A */
  const fullMonthRows = useMemo(() => {
    const days = getDaysInMonth(yearNum, monthNum);
    const byDate = new Map<string, AttendanceTableRow>();
    for (const r of apiRecords) {
      const key = toDateKey(r.date);
      if (key) byDate.set(key, r);
    }
    return days.map((dateStr) => {
      const existing = byDate.get(dateStr);
      if (existing) return existing;
      return { date: dateStr, status: 'NA', id: undefined } as AttendanceTableRow;
    });
  }, [yearNum, monthNum, apiRecords]);

  const columns = [
    {
      key: 'sno',
      header: 'S. No',
      align: 'right' as const,
      render: (_row: AttendanceTableRow, index: number) => (
        <span className="text-gray-500 dark:text-gray-400 font-medium tabular-nums">
          {index + 1}
        </span>
      ),
    },
    {
      key: 'day',
      header: 'Day',
      align: 'left' as const,
      render: (row: AttendanceTableRow) => (
        <span className="text-gray-700 dark:text-gray-300 font-medium">
          {getDayOfWeek(row.date)}
        </span>
      ),
    },
    {
      key: 'date',
      header: 'Date',
      align: 'left' as const,
      render: (row: AttendanceTableRow) => (
        <span className="text-gray-900 dark:text-gray-100">
          {formatDateShort(row.date)}
        </span>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      align: 'center' as const,
      render: (row: AttendanceTableRow) => (
        <div className="flex justify-center">
          <StatusBadge status={row.status} />
        </div>
      ),
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
      <AttendanceDetailsStats
        totalLeave={statsFromApi?.leave_days ?? 0}
        totalAbsent={statsFromApi?.absent_days ?? 0}
        workingDays={statsFromApi?.total_days ?? 0}
        presentDays={statsFromApi?.present_days ?? 0}
        halfDays={statsFromApi?.half_days ?? 0}
        attendanceRate={statsFromApi?.attendance_rate}
      />

      <div key={`table-${year}-${month}`}>
        <DataTable<AttendanceTableRow>
          columns={columns}
          data={fullMonthRows}
          emptyMessage="No dates in selected month"
          loading={isLoading}
          getRowKey={(row) => row.date}
        />
      </div>
    </div>
  );
}
