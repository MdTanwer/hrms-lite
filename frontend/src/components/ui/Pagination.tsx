// Fallback icons for pagination
const ChevronLeftIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
  </svg>
);

const ChevronRightIcon = ({ className }: { className?: string }) => (
  <svg
    className={className}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  pageSize: number;
  onPageSizeChange?: (pageSize: number) => void;
  totalItems: number;
  siblingCount?: number;
  boundaryCount?: number;
  showPageSizeSelector?: boolean;
  showInfo?: boolean;
  pageSizeOptions?: number[];
  className?: string;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  pageSize,
  onPageSizeChange,
  totalItems,
  siblingCount = 1,
  boundaryCount = 1,
  showPageSizeSelector = true,
  showInfo = true,
  pageSizeOptions = [10, 25, 50, 100],
  className = ''
}) => {
  const startItem = currentPage === 0 ? 1 : currentPage * pageSize + 1;
  const endItem = Math.min(startItem + pageSize - 1, totalItems);

  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    
    // Always show first page
    if (boundaryCount > 0) {
      for (let i = 1; i <= Math.min(boundaryCount, totalPages); i++) {
        pages.push(i);
      }
    }
    
    // Show ellipsis after first boundary if needed
    if (boundaryCount < currentPage - siblingCount) {
      pages.push('...');
    }
    
    // Show pages around current page
    const startPage = Math.max(boundaryCount + 1, currentPage - siblingCount);
    const endPage = Math.min(totalPages - boundaryCount, currentPage + siblingCount);
    
    for (let i = startPage; i <= endPage; i++) {
      if (i > 0 && i <= totalPages) {
        pages.push(i);
      }
    }
    
    // Show ellipsis before last boundary if needed
    if (currentPage + siblingCount < totalPages - boundaryCount) {
      pages.push('...');
    }
    
    // Always show last page
    if (boundaryCount > 0) {
      for (let i = Math.max(totalPages - boundaryCount + 1, boundaryCount + 1); i <= totalPages; i++) {
        pages.push(i);
      }
    }
    
    return pages;
  };

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      onPageChange(page);
    }
  };

  const handlePageSizeChange = (newPageSize: number) => {
    if (onPageSizeChange && newPageSize !== pageSize) {
      onPageSizeChange(newPageSize);
    }
  };

  const pages = getPageNumbers();

  return (
    <div className={`flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 ${className}`}>
      {/* Info */}
      {showInfo && (
        <div className="text-sm text-gray-700 dark:text-gray-300">
          Showing {startItem} to {endItem} of {totalItems} results
        </div>
      )}

      {/* Page Size Selector */}
      {showPageSizeSelector && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-700 dark:text-gray-300">Rows per page:</span>
          <select
            value={pageSize}
            onChange={(e) => handlePageSizeChange(Number(e.target.value))}
            className="rounded-md border border-gray-300 bg-white px-3 py-1 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
          >
            {pageSizeOptions.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Pagination Controls */}
      <div className="flex items-center gap-2">
        {/* Previous Button */}
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 0}
          className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
        >
          <span className="sr-only">Previous</span>
          <ChevronLeftIcon className="h-5 w-5" />
        </button>

        {/* Page Numbers */}
        <div className="flex items-center space-x-1">
          {pages.map((page, index) => (
            <button
              key={index}
              onClick={() => typeof page === 'number' && handlePageChange(page)}
              disabled={page === '...'}
              className={`relative inline-flex items-center px-3 py-2 text-sm font-medium ${
                page === currentPage
                  ? 'z-10 bg-blue-600 text-white border-blue-600'
                  : page === '...'
                  ? 'border-transparent text-gray-400 cursor-not-allowed'
                  : 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-800'
              }`}
            >
              {page}
            </button>
          ))}
        </div>

        {/* Next Button */}
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage >= totalPages - 1}
          className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
        >
          <span className="sr-only">Next</span>
          <ChevronRightIcon className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
};

export default Pagination;
