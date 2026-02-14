import { ReactNode } from 'react';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className = ''
}) => {
  return (
    <div className={`text-center py-12 px-4 ${className}`}>
      {icon && (
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center dark:bg-gray-800">
            {icon}
          </div>
        </div>
      )}
      <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
        {title}
      </h3>
      {description && (
        <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">
          {description}
        </p>
      )}
      {action && (
        <div className="flex justify-center">
          {action}
        </div>
      )}
    </div>
  );
};

export const EmployeesEmptyState: React.FC<{ onAddEmployee: () => void }> = ({ 
  onAddEmployee 
}) => {
  return (
    <EmptyState
      title="No employees found"
      description="Get started by adding your first employee to the system."
      action={
        <button
          onClick={onAddEmployee}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Add Employee
        </button>
      }
    />
  );
};

export const AttendanceEmptyState: React.FC<{ onMarkAttendance: () => void }> = ({ 
  onMarkAttendance 
}) => {
  return (
    <EmptyState
      title="No attendance records"
      description="Start tracking attendance by marking employee attendance."
      action={
        <button
          onClick={onMarkAttendance}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Mark Attendance
        </button>
      }
    />
  );
};

export default EmptyState;
