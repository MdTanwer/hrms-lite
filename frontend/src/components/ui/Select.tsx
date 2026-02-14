import { forwardRef } from 'react';
import { SelectProps, SelectOption } from '@/types/select.types';

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, helperText, options, fullWidth = true, className = '', placeholder, required, ...props }, ref) => {
    const baseClasses = 'rounded-md border px-3 py-2 text-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed bg-white dark:bg-gray-700 appearance-none pr-10';
    const stateClasses = error 
      ? 'border-red-300 text-red-900 focus:border-red-500 focus:ring-red-500 dark:border-red-600 dark:text-red-100 dark:focus:border-red-500 dark:focus:ring-red-500'
      : 'border-gray-300 text-gray-900 hover:border-gray-400 dark:border-gray-600 dark:text-gray-100 dark:hover:border-gray-500';
    const widthClasses = fullWidth ? 'w-full' : '';

    const classes = [
      baseClasses,
      stateClasses,
      widthClasses,
      className
    ].filter(Boolean).join(' ');

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
            {label}
            {required && (
              <span className="ml-0.5 text-red-500 dark:text-red-400" aria-hidden>*</span>
            )}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            className={classes}
            required={required}
            {...props}
          >
            {placeholder && (
              <option value="" disabled className="dark:bg-gray-800 dark:text-gray-100">
                {placeholder}
              </option>
            )}
            {options.map((option: SelectOption) => (
              <option 
                key={option.value} 
                value={option.value} 
                disabled={option.disabled}
                className="dark:bg-gray-800 dark:text-gray-100"
              >
                {option.label}
              </option>
            ))}
          </select>
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
            <svg 
              className="w-4 h-4 text-gray-400 dark:text-gray-500" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M19 9l-7 7-7-7" 
              />
            </svg>
          </div>
        </div>
        {error && (
          <p className="mt-1 text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Select.displayName = 'Select';

export default Select;
