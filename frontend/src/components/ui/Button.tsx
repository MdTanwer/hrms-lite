import React from 'react';
import { ButtonProps } from '@/types/button.types';

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-all duration-200 cursor-pointer border-2 whitespace-nowrap relative overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900';
  
  const variantClasses = {
    primary: 'bg-blue-500 text-white border-blue-500 hover:bg-blue-600 hover:border-blue-600 focus:ring-blue-500 focus:border-blue-600 dark:bg-blue-600 dark:border-blue-600 dark:hover:bg-blue-700 dark:hover:border-blue-700 dark:focus:ring-blue-500',
    secondary: 'bg-gray-500 text-white border-gray-500 hover:bg-gray-600 hover:border-gray-600 focus:ring-gray-500 focus:border-gray-600 dark:bg-gray-600 dark:border-gray-600 dark:hover:bg-gray-700 dark:hover:border-gray-700 dark:focus:ring-gray-500',
    outline: 'bg-transparent text-blue-500 border-blue-500 hover:bg-blue-500 hover:text-white focus:ring-blue-500 focus:border-blue-600 dark:text-blue-400 dark:border-blue-400 dark:hover:bg-blue-400 dark:hover:text-white dark:focus:ring-blue-400 dark:focus:border-blue-500',
    ghost: 'bg-transparent text-gray-500 border-transparent hover:bg-gray-100 hover:text-gray-700 focus:ring-gray-500 focus:border-gray-300 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-200 dark:focus:ring-gray-400 dark:focus:border-gray-600',
    destructive: '!bg-red-600 !text-white !border-red-600 hover:!bg-red-700 hover:!border-red-700 focus:!ring-red-500 focus:!border-red-700 dark:!bg-red-700 dark:!border-red-700 dark:hover:!bg-red-800 dark:hover:!border-red-800 dark:focus:!ring-red-500'
  }[variant];

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm min-h-[2rem]',
    md: 'px-4 py-2 text-sm min-h-[2.5rem]',
    lg: 'px-6 py-3 text-base min-h-[3rem]'
  }[size];

  const widthClasses = fullWidth ? 'w-full' : '';
  const loadingClasses = loading ? 'cursor-wait' : '';
  
  const classes = [
    baseClasses,
    variantClasses,
    sizeClasses,
    widthClasses,
    loadingClasses,
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg 
          className="w-4 h-4 animate-spin" 
          xmlns="http://www.w3.org/2000/svg" 
          fill="none" 
          viewBox="0 0 24 24"
        >
          <circle 
            className="opacity-25" 
            cx="12" 
            cy="12" 
            r="10" 
            stroke="currentColor" 
            strokeWidth="4"
          />
          <path 
            className="opacity-75" 
            fill="currentColor" 
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      <span className={loading ? 'opacity-70' : ''}>
        {children}
      </span>
    </button>
  );
};

export default Button;