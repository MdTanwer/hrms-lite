import { Link } from "react-router";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4 text-center">
      <p className="text-6xl font-bold text-gray-200 dark:text-gray-600">404</p>
      <h1 className="mt-4 text-xl font-semibold text-gray-900 dark:text-gray-100">
        Page not found
      </h1>
      <p className="mt-2 max-w-sm text-gray-600 dark:text-gray-400">
        The page you’re looking for doesn’t exist or has been moved.
      </p>
      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Link
          to="/"
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
        >
          Go to Dashboard
        </Link>
        <Link
          to="/employees"
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-800"
        >
          Employees
        </Link>
      </div>
    </div>
  );
}
