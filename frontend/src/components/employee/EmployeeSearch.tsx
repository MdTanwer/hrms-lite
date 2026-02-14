import React from 'react';

interface EmployeeSearchProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
}

const EmployeeSearch: React.FC<EmployeeSearchProps> = ({
  searchTerm,
  onSearchChange
}) => {
  return (
    <div className="relative">
      <input
        type="text"
        placeholder="Search employees..."
        value={searchTerm}
        onChange={(e) => onSearchChange(e.target.value)}
        className="w-full rounded-md border border-gray-300 bg-white pl-10 pr-3 py-2 text-sm text-gray-900 placeholder-gray-500 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-100 dark:placeholder-gray-400 dark:focus:border-blue-400 dark:focus:ring-blue-400 transition-all duration-200"
      />
      {/* Search Icon */}
      <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
    </div>
  );
};

export default EmployeeSearch;
