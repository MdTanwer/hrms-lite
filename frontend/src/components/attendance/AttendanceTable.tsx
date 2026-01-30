import { DataTable } from '../table/DataTable';
import { AttendanceCell, StatusBadge, DateCell } from './AttendanceRow';
import { Attendance } from '../../types/attendance';
import { Employee } from '../../types/employee';

interface AttendanceTableProps {
  attendances: (Attendance & { employee: Employee })[];
  loading?: boolean;
  emptyAction?: React.ReactNode;
}

const AttendanceTable: React.FC<AttendanceTableProps> = ({ 
  attendances, 
  loading = false,
  emptyAction 
}) => {
  const columns = [
    {
      key: "employee",
      header: "Employee",
      render: (row: any) => <AttendanceCell employee={row.employee} />
    },
    {
      key: "date",
      header: "Date",
      render: (row: any) => <DateCell date={row.date} />
    },
    {
      key: "department",
      header: "Department",
      render: (row: any) => row.employee.department
    },
    {
      key: "position",
      header: "Position",
      render: (row: any) => row.employee.position
    },
    {
      key: "status",
      header: "Status",
      render: (row: any) => <StatusBadge status={row.status} />
    },
    {
      key: "actions",
      header: "Actions",
      render: () => (
        <>
          <button className="text-blue-600 hover:text-blue-800 mr-3 dark:text-blue-400 dark:hover:text-blue-300">
            Edit
          </button>
          <button className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
            Delete
          </button>
        </>
      )
    }
  ];

  return (
    <DataTable
      columns={columns}
      data={attendances}
      loading={loading}
      emptyMessage="No attendance records found"
      emptyAction={emptyAction}
    />
  );
};

export default AttendanceTable;
