import { AlertProps } from '@/types/alert.types';
import { CheckCircleIcon, AlertIcon, ErrorIcon, InfoIcon } from '@/icons';

const Alert: React.FC<AlertProps> = ({
  type,
  title,
  children,
  dismissible = false,
  onDismiss,
  className = ''
}) => {
  const alertStyles = {
    success: 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300',
    error: 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-300',
    info: 'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300'
  };

  const icons = {
    success: <CheckCircleIcon className="w-5 h-5 text-green-500 dark:text-green-400" />,
    error: <ErrorIcon className="w-5 h-5 text-red-500 dark:text-red-400" />,
    warning: <AlertIcon className="w-5 h-5 text-yellow-500 dark:text-yellow-400" />,
    info: <InfoIcon className="w-5 h-5 text-blue-500 dark:text-blue-400" />
  };

  return (
    <div className={`border rounded-lg p-4 ${alertStyles[type]} ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          {icons[type]}
        </div>
        <div className="ml-3 flex-1">
          {title && (
            <h3 className="text-sm font-medium mb-1 dark:text-current">{title}</h3>
          )}
          <div className="text-sm dark:text-current/90">{children}</div>
        </div>
        {dismissible && onDismiss && (
          <div className="ml-auto pl-3">
            <button
              onClick={onDismiss}
              className="inline-flex text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-current dark:text-gray-500 dark:hover:text-gray-300 dark:focus:ring-offset-gray-800"
            >
              <span className="sr-only">Dismiss</span>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alert;
