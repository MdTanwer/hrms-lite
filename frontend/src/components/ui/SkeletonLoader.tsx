interface SkeletonLoaderProps {
  lines?: number;
  className?: string;
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ 
  lines = 3, 
  className = '' 
}) => {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <div key={index} className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded dark:bg-gray-700 w-full"></div>
        </div>
      ))}
    </div>
  );
};

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => {
  return (
    <div className="space-y-4">
      <div className="animate-pulse">
        <div className="h-10 bg-gray-200 rounded dark:bg-gray-700 w-full"></div>
      </div>
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="animate-pulse">
          <div className="h-16 bg-gray-100 rounded dark:bg-gray-800 w-full"></div>
        </div>
      ))}
    </div>
  );
};

export const CardSkeleton: React.FC<{ cards?: number }> = ({ cards = 6 }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {Array.from({ length: cards }).map((_, index) => (
        <div key={index} className="animate-pulse">
          <div className="h-20 bg-gray-200 rounded-lg dark:bg-gray-700"></div>
        </div>
      ))}
    </div>
  );
};

export default SkeletonLoader;
