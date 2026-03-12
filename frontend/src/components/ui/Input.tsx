import { forwardRef } from 'react';
import { InputProps } from '@/types/input.types';

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, startIcon, endIcon, fullWidth = true, className = '', required, ...props }, ref) => {
    const baseClasses = 'rounded-md border px-3 py-2 text-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed';
    const stateClasses = error
      ? 'border-red-300 bg-red-50 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500 dark:border-red-600 dark:bg-red-900/20 dark:text-red-100 dark:placeholder-red-400 dark:focus:border-red-500 dark:focus:ring-red-500 [&:-webkit-autofill]:!bg-red-50 [&:-webkit-autofill]:!shadow-[0_0_0px_1000px_rgba(254,226,226,1)] dark:[&:-webkit-autofill]:!shadow-[0_0_0px_1000px_rgba(127,29,29,0.3)]'
      : 'border-gray-300 bg-white text-gray-900 placeholder-gray-500 hover:border-gray-400 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 dark:placeholder-gray-400 dark:hover:border-gray-500';
    const widthClasses = fullWidth ? 'w-full' : '';
    const iconPaddingClasses = {
      start: startIcon ? 'pl-10' : '',
      end: endIcon ? 'pr-10' : '',
    };

    const classes = [
      baseClasses,
      widthClasses,
      iconPaddingClasses.start,
      iconPaddingClasses.end,
      className,
      stateClasses,
    ].filter(Boolean).join(' ');

    return (
      <div className={fullWidth ? 'w-full' : ''}>
        {label && (
          <label className="block text-sm font-medium text-gray-700 mb-1 dark:text-gray-300">
            {label}
            {required && (
              <span className="ml-0.5 text-red-500 dark:text-red-400" aria-hidden>
                *
              </span>
            )}
          </label>
        )}
        <div className="relative">
          {startIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <div className="text-gray-400 dark:text-gray-500">
                {startIcon}
              </div>
            </div>
          )}
          <input
            ref={ref}
            className={classes}
            required={required}
            {...props}
          />
          {endIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <div className="text-gray-400 dark:text-gray-500">
                {endIcon}
              </div>
            </div>
          )}
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

Input.displayName = 'Input';

export default Input;