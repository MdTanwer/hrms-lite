import { useState, useRef, useEffect } from 'react';
import Input from '@/components/ui/Input';

export interface SearchableSelectOption {
  value: string;
  label: string;
}

interface SearchableSelectProps {
  label?: string;
  options: SearchableSelectOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  fullWidth?: boolean;
  error?: boolean;
  searchPlaceholder?: string;
  /** When true (default), filter options by search query locally. When false, options are already filtered by backend. */
  filterLocally?: boolean;
  /** Controlled search input; use with onSearchChange for backend search */
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
}

export default function SearchableSelect({
  label,
  options,
  value,
  onChange,
  placeholder = 'Select...',
  required = false,
  fullWidth = true,
  error = false,
  searchPlaceholder = 'Search...',
  filterLocally = true,
  searchQuery: controlledSearchQuery,
  onSearchChange,
}: SearchableSelectProps) {
  const [open, setOpen] = useState(false);
  const [internalSearch, setInternalSearch] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  const searchQuery = controlledSearchQuery ?? internalSearch;
  const setSearchQuery = onSearchChange ?? setInternalSearch;

  const selectedOption = options.find((opt) => opt.value === value);
  const displayText = selectedOption ? selectedOption.label : '';

  const filteredOptions = filterLocally
    ? options.filter((opt) =>
        opt.label.toLowerCase().includes(searchQuery.trim().toLowerCase())
      )
    : options;

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (opt: SearchableSelectOption) => {
    onChange(opt.value);
    setSearchQuery('');
    setInternalSearch('');
    setOpen(false);
  };

  const handleTriggerClick = () => {
    setOpen((prev) => !prev);
    if (!open) {
      setSearchQuery('');
      setInternalSearch('');
    }
  };

  const triggerBaseClasses =
    'rounded-md border px-3 py-2 text-sm transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50 disabled:cursor-not-allowed w-full text-left flex items-center justify-between bg-white dark:bg-gray-700 cursor-pointer';
  const triggerStateClasses = error
    ? 'border-red-300 text-red-900 dark:border-red-600 dark:text-red-100'
    : 'border-gray-300 text-gray-900 hover:border-gray-400 dark:border-gray-600 dark:text-gray-100 dark:hover:border-gray-500';

  return (
    <div className={fullWidth ? 'w-full' : ''} ref={containerRef}>
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
        <button
          type="button"
          onClick={handleTriggerClick}
          className={`${triggerBaseClasses} ${triggerStateClasses}`}
          aria-expanded={open}
          aria-haspopup="listbox"
        >
          <span className={displayText ? 'text-gray-900 dark:text-gray-100' : 'text-gray-500 dark:text-gray-400'}>
            {displayText || placeholder}
          </span>
          <svg
            className={`w-4 h-4 text-gray-400 dark:text-gray-500 shrink-0 transition-transform ${open ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {open && (
          <div className="absolute z-50 mt-1 w-full rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-gray-800 py-1 min-w-[200px] max-h-64 flex flex-col">
            <div className="px-2 pb-2 border-b border-gray-200 dark:border-gray-700">
              <Input
                type="text"
                placeholder={searchPlaceholder}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                fullWidth
                className="text-sm"
                autoFocus
                onKeyDown={(e) => e.stopPropagation()}
              />
            </div>
            <ul
              className="overflow-y-auto py-1"
              role="listbox"
            >
              {filteredOptions.length === 0 ? (
                <li className="px-3 py-2 text-sm text-gray-500 dark:text-gray-400">No results</li>
              ) : (
                filteredOptions.map((opt) => (
                  <li
                    key={opt.value}
                    role="option"
                    aria-selected={opt.value === value}
                    onClick={() => handleSelect(opt)}
                    className={`px-3 py-2 text-sm cursor-pointer ${
                      opt.value === value
                        ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300'
                        : 'text-gray-900 hover:bg-gray-100 dark:text-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    {opt.label}
                  </li>
                ))
              )}
            </ul>
          </div>
        )}
      </div>
      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400">This field is required.</p>
      )}
    </div>
  );
}
