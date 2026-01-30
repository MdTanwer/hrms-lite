import { CardSkeleton } from '../ui/SkeletonLoader';

interface AttendanceStatsProps {
  total: number;
  present: number;
  absent: number;
  late: number;
  halfDay: number;
  attendanceRate: number;
  loading?: boolean;
}

const AttendanceStats: React.FC<AttendanceStatsProps> = ({
  total,
  present,
  absent,
  late,
  halfDay,
  attendanceRate,
  loading = false
}) => {
  if (loading) {
    return <CardSkeleton cards={6} />;
  }

  const statCards = [
    {
      title: 'Total Days',
      value: total,
      color: 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'
    },
    {
      title: 'Present',
      value: present,
      color: 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300'
    },
    {
      title: 'Absent',
      value: absent,
      color: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300'
    },
    {
      title: 'Late',
      value: late,
      color: 'bg-yellow-50 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-300'
    },
    {
      title: 'Half Day',
      value: halfDay,
      color: 'bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300'
    },
    {
      title: 'Attendance Rate',
      value: `${attendanceRate}%`,
      color: 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/20 dark:text-indigo-300'
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {statCards.map((stat, index) => (
        <div
          key={index}
          className={`rounded-lg p-4 text-center ${stat.color}`}
        >
          <div className="text-2xl font-bold">{stat.value}</div>
          <div className="text-sm font-medium">{stat.title}</div>
        </div>
      ))}
    </div>
  );
};

export default AttendanceStats;
