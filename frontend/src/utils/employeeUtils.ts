import { Employee } from "../types/employee";

export const getStatusColor = (status: Employee["status"]) => {
  const map = {
    active: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
    inactive: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
    "on-leave": "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300"
  };
  return map[status] || "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-300";
};
