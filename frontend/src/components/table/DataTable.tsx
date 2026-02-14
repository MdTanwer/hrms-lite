import { TableSkeleton } from '@/components/ui/SkeletonLoader';
import EmptyState from '@/components/ui/EmptyState';

type Column<T> = {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
};

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  emptyMessage?: string;
  loading?: boolean;
  emptyAction?: React.ReactNode;
}

export function DataTable<T>({
  columns,
  data,
  emptyMessage = "No records found",
  loading = false,
  emptyAction
}: DataTableProps<T>) {
  if (loading) {
    return <TableSkeleton rows={5} />;
  }

  if (!data.length) {
    return (
      <EmptyState
        title={emptyMessage}
        description="There are no records to display at the moment."
        action={emptyAction}
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            {columns.map(col => (
              <th
                key={col.key as string}
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase dark:text-gray-400"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>

        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {data.map((row, idx) => (
            <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
              {columns.map(col => (
                <td key={col.key as string} className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                  {col.render
                    ? col.render(row)
                    : (row as any)[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
