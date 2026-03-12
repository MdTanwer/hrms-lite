import { Attendance } from "@/types/attendance";

export const getAttendanceColor = (status: string) => {
  const map: Record<string, string> = {
    "present": "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    "absent": "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
    "half-day": "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
    "leave": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
  };
  return map[status] || "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300";
};

/** Row background by status for table (absent=red, present=green, etc.; empty/unknown=neutral) */
export const getAttendanceRowClass = (status: string): string => {
  const map: Record<string, string> = {
    present: "bg-green-50 dark:bg-green-900/20 border-l-4 border-green-400",
    absent: "bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400",
    "half-day": "bg-amber-50 dark:bg-amber-900/20 border-l-4 border-amber-400",
    leave: "bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-400",
  };
  return map[status] || "bg-gray-50 dark:bg-gray-800/30 border-l-4 border-gray-300 dark:border-gray-600";
};

export const getAttendanceIcon = (status: string) => {
  const map: Record<string, string> = {
    "present": "✓",
    "absent": "✗",
    "half-day": "½",
    "leave": "L"
  };
  return map[status] || "?";
};

export const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

export const getTodayDate = () => {
  return new Date().toISOString().split('T')[0];
};

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
