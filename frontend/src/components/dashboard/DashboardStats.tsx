import { CardSkeleton } from '@/components/ui/SkeletonLoader';

interface DashboardStatsProps {
  totalEmployees: number;
  activeEmployees: number;
  totalDepartments: number;
  presentToday: number;
  absentToday: number;
  attendanceRate: number;
  loading?: boolean;
}

const DashboardStats: React.FC<DashboardStatsProps> = ({
  totalEmployees,
  activeEmployees,
  totalDepartments,
  presentToday,
  absentToday,
  attendanceRate,
  loading = false
}) => {
  if (loading) {
    return <CardSkeleton cards={5} />;
  }

  const statCards = [
    {
      title: 'Total Employees',
      value: totalEmployees,
      icon: '👥',
      color: 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300',
      trend: '+2 this month'
    },
    {
      title: 'Active Employees',
      value: activeEmployees,
      icon: '✅',
      color: 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300',
      trend: `${Math.round((activeEmployees / totalEmployees) * 100)}% active`
    },
    {
      title: 'Departments',
      value: totalDepartments,
      icon: '🏢',
      color: 'bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300',
      trend: 'All operational'
    },
    {
      title: 'Present Today',
      value: presentToday,
      icon: '📅',
      color: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
      trend: `${attendanceRate}% attendance rate`
    },
    {
      title: 'Absent Today',
      value: absentToday,
      icon: '❌',
      color: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300',
      trend: 'Need follow-up'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
      {statCards.map((stat, index) => (
        <div
          key={index}
          className={`rounded-xl p-6 ${stat.color} transition-all duration-200 hover:scale-105`}
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-2xl">{stat.icon}</span>
            <div className="text-xs font-medium opacity-75">
              {stat.trend}
            </div>
          </div>
          <div className="text-3xl font-bold mb-1">{stat.value}</div>
          <div className="text-sm font-medium">{stat.title}</div>
        </div>
      ))}
    </div>
  );
};

export default DashboardStats;
