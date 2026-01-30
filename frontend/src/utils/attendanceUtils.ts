import { Attendance } from "../types/attendance";

export const getAttendanceColor = (status: Attendance["status"]) => {
  const map = {
    present: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    absent: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
    late: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300",
    "half-day": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
  };
  return map[status] || "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300";
};

export const getAttendanceIcon = (status: Attendance["status"]) => {
  const map = {
    present: "✓",
    absent: "✗",
    late: "⏰",
    "half-day": "◐"
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
    present: 0,
    absent: 0,
    late: 0,
    halfDay: 0,
    total: attendances.length
  };

  attendances.forEach(att => {
    switch (att.status) {
      case 'present':
        stats.present++;
        break;
      case 'absent':
        stats.absent++;
        break;
      case 'late':
        stats.late++;
        break;
      case 'half-day':
        stats.halfDay++;
        break;
    }
  });

  const attendanceRate = stats.total > 0 ? (stats.present / stats.total) * 100 : 0;

  return {
    ...stats,
    attendanceRate: Math.round(attendanceRate * 100) / 100
  };
};
