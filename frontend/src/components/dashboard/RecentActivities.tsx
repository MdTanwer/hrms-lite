import SkeletonLoader from '@/components/ui/SkeletonLoader';

interface Activity {
  id: string;
  employeeId: string;
  employeeName: string;
  employeeDepartment: string;
  date: string;
  status: string;
  markedAt: string;
}

interface RecentActivitiesProps {
  activities: Activity[];
  loading?: boolean;
}

const RecentActivities: React.FC<RecentActivitiesProps> = ({ 
  activities, 
  loading = false 
}) => {
  if (loading) {
    return <SkeletonLoader lines={5} className="h-64" />;
  }

  const getStatusColor = (status: string) => {
    const colors = {
      present: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      absent: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
      late: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
      'half-day': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
        Recent Activities
      </h3>
      
      <div className="space-y-4">
        {activities.map((activity) => (
          <div key={activity.id} className="flex items-start justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-xs font-medium text-blue-600 dark:text-blue-300">
                  {activity.employeeName.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {activity.employeeName}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {activity.employeeDepartment}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                    {activity.status.charAt(0).toUpperCase() + activity.status.slice(1)}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {formatDate(activity.markedAt)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {activities.length === 0 && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <p>No recent activities</p>
        </div>
      )}
    </div>
  );
};

export default RecentActivities;
