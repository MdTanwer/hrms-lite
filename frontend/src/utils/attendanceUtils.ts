import { Attendance } from "../types/attendance";

export const getAttendanceColor = (status: string) => {
  const map = {
    "present": "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    "absent": "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300"
  };
  return map[status as keyof typeof map] || "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300";
};

export const getAttendanceIcon = (status: string) => {
  const map = {
    "present": "✓",
    "absent": "✗"
  };
  return map[status as keyof typeof map] || "?";
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
