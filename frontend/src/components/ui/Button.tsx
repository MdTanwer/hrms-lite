import React from 'react';
import { ButtonProps } from '../../types/button.types';

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
  const baseClasses = 'inline-flex items-center justify-center gap-2 rounded-md font-medium transition-all duration-200 cursor-pointer border whitespace-nowrap relative overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-blue-500 text-white border-blue-500 hover:bg-blue-600 hover:border-blue-600',
    secondary: 'bg-gray-500 text-white border-gray-500 hover:bg-gray-600 hover:border-gray-600',
    outline: 'bg-transparent text-blue-500 border-blue-500 hover:bg-blue-500 hover:text-white',
    ghost: 'bg-transparent text-gray-500 border-transparent hover:bg-gray-100 hover:text-gray-700',
    destructive: 'bg-red-500 text-white border-red-500 hover:bg-red-600 hover:border-red-600'
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