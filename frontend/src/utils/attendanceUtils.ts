import { Attendance } from "@/types/attendance";

/** N/A = not marked / future date; use neutral muted style */
export const getAttendanceColor = (status: string) => {
  const s = (status || '').toLowerCase();
  if (s === 'na' || s === 'n/a' || s === '') {
    return "bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400";
  }
  const map: Record<string, string> = {
    "present": "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    "absent": "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
    "half-day": "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
    "leave": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
  };
  return map[s] || "bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400";
};

/** Row background by status for table (absent=red, present=green, etc.; NA=neutral muted) */
export const getAttendanceRowClass = (status: string): string => {
  const s = (status || '').toLowerCase();
  if (s === 'na' || s === 'n/a' || s === '') {
    return "bg-white dark:bg-gray-800/50 border-l-4 border-gray-200 dark:border-gray-600";
  }
  const map: Record<string, string> = {
    present: "bg-green-50/80 dark:bg-green-900/20 border-l-4 border-green-500",
    absent: "bg-red-50/80 dark:bg-red-900/20 border-l-4 border-red-500",
    "half-day": "bg-amber-50/80 dark:bg-amber-900/20 border-l-4 border-amber-500",
    leave: "bg-blue-50/80 dark:bg-blue-900/20 border-l-4 border-blue-500",
  };
  return map[s] || "bg-white dark:bg-gray-800/50 border-l-4 border-gray-200 dark:border-gray-600";
};

export const getAttendanceIcon = (status: string) => {
  const s = (status || '').toLowerCase();
  if (s === 'na' || s === 'n/a' || s === '') return "—";
  const map: Record<string, string> = {
    "present": "✓",
    "absent": "✗",
    "half-day": "½",
    "leave": "L"
  };
  return map[s] ?? "—";
};

export const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

/** Short format for tables: "2 Feb 2026" */
export const formatDateShort = (date: string) => {
  return new Date(date + 'T12:00:00').toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  });
};

export const getTodayDate = () => {
  return new Date().toISOString().split('T')[0];
};

/** Date to YYYY-MM-DD in local time. */
export function toLocalDateString(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/** First and last day of month as YYYY-MM-DD (for API range). */
export function getMonthStartEnd(year: number, month: number) {
  const start = new Date(year, month - 1, 1);
  const end = new Date(year, month, 0);
  return {
    startDate: toLocalDateString(start),
    endDate: toLocalDateString(end),
  };
}

/** All calendar days in the month as YYYY-MM-DD (1 through last day). */
export function getDaysInMonth(year: number, month: number): string[] {
  const lastDay = new Date(year, month, 0).getDate();
  const out: string[] = [];
  for (let d = 1; d <= lastDay; d++) {
    out.push(toLocalDateString(new Date(year, month - 1, d)));
  }
  return out;
}

/** Normalize API date (ISO or YYYY-MM-DD) to YYYY-MM-DD for map key. */
export function toDateKey(dateStr: string): string {
  if (!dateStr) return '';
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return dateStr.slice(0, 10);
  return toLocalDateString(d);
}

/** Short day-of-week label (Mon, Tue, …). */
export function getDayOfWeek(dateStr: string): string {
  const d = new Date(dateStr + 'T12:00:00');
  return d.toLocaleDateString('en-US', { weekday: 'short' });
}

/** Year options for dropdown: current year and previous 4. */
export function getYears(): { value: string; label: string }[] {
  const current = new Date().getFullYear();
  return Array.from({ length: 5 }, (_, i) => ({
    value: String(current - i),
    label: String(current - i),
  }));
}

export const calculateAttendanceStats = (attendances: Attendance[]) => {
  const stats = {
    total: attendances.length,
    present: 0,
    absent: 0
  };

  attendances.forEach(att => {
    switch (att.status) {
      case 'present':
        stats.present++;
        break;
      case 'absent':
        stats.absent++;
        break;
    }
  });

  const attendanceRate = stats.total > 0 ? (stats.present / stats.total) * 100 : 0;

  return {
    ...stats,
    attendanceRate: Math.round(attendanceRate * 100) / 100
  };
};
