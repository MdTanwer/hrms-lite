import { ErrorIcon } from "@/icons";
import { getApiErrorMessage } from "@/utils/apiErrorHandler";

export interface ErrorStateProps {
  /** Short title for the error (e.g. "Error loading employees") */
  title: string;
  /** API or JS error; message is derived via handleApiError */
  error: unknown;
  /** Optional retry callback; when provided, a retry button is shown */
  onRetry?: () => void;
  /** Optional class for the outer wrapper */
  className?: string;
}

/**
 * Central, reusable error state for API failures. Use on pages when a query fails.
 */
export default function ErrorState({
  title,
  error,
  onRetry,
  className = "",
}: ErrorStateProps) {
  const message = getApiErrorMessage(error);

  return (
    <div className={`p-6 ${className}`.trim()}>
      <div
        role="alert"
        className="flex gap-4 rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20"
      >
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/40">
          <ErrorIcon className="h-5 w-5 text-red-600 dark:text-red-400" />
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="font-medium text-red-800 dark:text-red-400">{title}</h3>
          <p className="mt-1 text-sm text-red-600 dark:text-red-300">{message}</p>
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="mt-3 rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
            >
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
