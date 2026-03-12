import SkeletonLoader from '@/components/ui/SkeletonLoader';

interface DepartmentChartProps {
  departmentStats: Record<string, number>;
  loading?: boolean;
}

const DepartmentChart: React.FC<DepartmentChartProps> = ({ 
  departmentStats, 
  loading = false 
}) => {
  if (loading) {
    return <SkeletonLoader lines={5} className="h-64" />;
  }

  const totalEmployees = Object.values(departmentStats).reduce((sum, count) => sum + count, 0);
  
  const departmentData = Object.entries(departmentStats).map(([department, count]) => ({
    name: department,
    count,
    percentage: Math.round((count / totalEmployees) * 100)
  }));

  const colors = [
    'bg-blue-500',
    'bg-green-500', 
    'bg-purple-500',
    'bg-amber-500',
    'bg-red-500',
    'bg-indigo-500'
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
        Department Distribution
      </h3>
      
      <div className="space-y-4">
        {departmentData.map((dept, index) => (
          <div key={dept.name} className="flex items-center justify-between">
            <div className="flex items-center flex-1">
              <div className={`w-3 h-3 rounded-full ${colors[index % colors.length]} mr-3`} />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {dept.name}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${colors[index % colors.length]}`}
                  style={{ width: `${dept.percentage}%` }}
                />
              </div>
              <span className="text-sm text-gray-600 dark:text-gray-400 w-12 text-right">
                {dept.count}
              </span>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600 dark:text-gray-400">Total Employees</span>
          <span className="font-semibold text-gray-900 dark:text-gray-100">
            {totalEmployees}
          </span>
        </div>
      </div>
    </div>
  );
};

export default DepartmentChart;
