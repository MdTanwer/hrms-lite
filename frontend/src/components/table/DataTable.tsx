import { TableSkeleton } from '@/components/ui/SkeletonLoader';
import EmptyState from '@/components/ui/EmptyState';

type ColumnAlign = 'left' | 'center' | 'right';

type Column<T> = {
  key: keyof T | string;
  header: string;
  align?: ColumnAlign;
  render?: (row: T, index: number) => React.ReactNode;
};

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  emptyMessage?: string;
  loading?: boolean;
  emptyAction?: React.ReactNode;
  /** Optional sticky footer (renders in tfoot) */
  footer?: React.ReactNode;
  /** Optional row class by row (e.g. status-based background) */
  getRowClassName?: (row: T, index: number) => string;
  /** Stable row key for React (e.g. row.date or row.id) */
  getRowKey?: (row: T, index: number) => string | number;
}

const alignClass: Record<ColumnAlign, string> = {
  left: 'text-left',
  center: 'text-center',
  right: 'text-right',
};

export function DataTable<T>({
  columns,
  data,
  emptyMessage = "No records found",
  loading = false,
  emptyAction,
  footer,
  getRowClassName,
  getRowKey,
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
    <div
      className="overflow-auto max-h-[70vh] data-table-scroll"
      style={
        {
          scrollbarWidth: 'thin',
          scrollbarGutter: 'stable',
        } as React.CSSProperties
      }
    >
      <table className="w-full">
        <thead className="sticky top-0 z-10 bg-gray-50 dark:bg-gray-700/50 shadow-[0_1px_0_0_rgba(0,0,0,0.05)] dark:shadow-[0_1px_0_0_rgba(255,255,255,0.06)]">
          <tr>
            {columns.map(col => (
              <th
                key={col.key as string}
                className={`px-6 py-3 text-xs font-medium text-gray-500 uppercase dark:text-gray-400 ${alignClass[col.align ?? 'left']}`}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {data.map((row, idx) => {
            const key = getRowKey ? getRowKey(row, idx) : idx;
            const rowClass = getRowClassName?.(row, idx) ?? 'hover:bg-gray-50 dark:hover:bg-gray-700/50';
            return (
              <tr key={key} className={rowClass}>
                {columns.map(col => (
                  <td
                    key={col.key as string}
                    className={`px-6 py-4 text-sm text-gray-900 dark:text-gray-100 ${alignClass[col.align ?? 'left']}`}
                  >
                    {col.render
                      ? col.render(row, idx)
                      : (row as Record<string, unknown>)[col.key as string] as React.ReactNode}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
        {footer != null && (
          <tfoot className="sticky bottom-0 z-10 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-600 shadow-[0_-1px_0_0_rgba(0,0,0,0.05)] dark:shadow-[0_-1px_0_0_rgba(255,255,255,0.06)]">
            <tr>
              <td colSpan={columns.length} className="px-6 py-3">
                {footer}
              </td>
            </tr>
          </tfoot>
        )}
      </table>
    </div>
  );
}
