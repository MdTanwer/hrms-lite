import { useMemo } from "react";
import PageMeta from "@/components/common/PageMeta";
import PageBreadCrumb from "@/components/common/PageBreadCrumb";
import DashboardStats from "@/components/dashboard/DashboardStats";
import DepartmentChart from "@/components/dashboard/DepartmentChart";
import RecentActivities from "@/components/dashboard/RecentActivities";
import { useEmployees } from "@/hooks/queries/useEmployees";
import { useAttendanceByDate } from "@/hooks/queries/useAttendance";

const today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD

export default function Home() {
  const { data: employeeList, isLoading: employeesLoading } = useEmployees({ limit: 500 });
  const { data: attendanceByDate, isLoading: attendanceLoading } = useAttendanceByDate(today);

  const loading = employeesLoading || attendanceLoading;

  const stats = useMemo(() => {
    const list = employeeList?.data ?? [];
    const totalEmployees = employeeList?.total ?? list.length;
    const activeEmployees = list.filter((e) => (e as { status?: string }).status === "active").length;
    const departmentBreakdown = list.reduce<Record<string, number>>((acc, e) => {
      const d = e.department ?? "Unknown";
      acc[d] = (acc[d] ?? 0) + 1;
      return acc;
    }, {});
    const totalDepartments = Object.keys(departmentBreakdown).length;

    const records = attendanceByDate?.data ?? [];
    const presentToday = records.filter((r) => (r.status ?? (r as any).status) === "present").length;
    const absentToday = records.filter((r) => (r.status ?? (r as any).status) === "absent").length;
    const attendanceRate =
      records.length > 0 ? Math.round((presentToday / records.length) * 100) : 0;

    const recentActivities = records
      .slice(0, 5)
      .map((r) => ({
        id: r.id ?? (r as any).id,
        employeeId: r.employeeId ?? (r as any).employee_id ?? "",
        employeeName: "Employee",
        employeeDepartment: "",
        date: r.date ?? (r as any).date ?? today,
        status: r.status ?? (r as any).status ?? "present",
        markedAt: r.markedAt ?? (r as any).marked_at ?? new Date().toISOString(),
      }));

    return {
      totalEmployees,
      activeEmployees,
      totalDepartments,
      presentToday,
      absentToday,
      attendanceRate,
      departmentStats: departmentBreakdown,
      recentActivities,
    };
  }, [employeeList, attendanceByDate]);

  return (
    <>
      <PageMeta
        title="HRMS Dashboard | HRMS Lite"
        description="HRMS Lite Dashboard - Complete overview of employee management and attendance tracking"
      />
      
      <PageBreadCrumb pageTitle="Dashboard" />
      
      <div className="grid grid-cols-12 gap-4 md:gap-6">
        {/* Header Section */}
        <div className="col-span-12">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  Welcome to HRMS Dashboard
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  Manage your workforce efficiently with real-time insights
                </p>
              </div>
              <div className="mt-4 sm:mt-0">
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Last updated: {new Date().toLocaleString()}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="col-span-12">
          <DashboardStats
            totalEmployees={stats.totalEmployees}
            activeEmployees={stats.activeEmployees}
            totalDepartments={stats.totalDepartments}
            presentToday={stats.presentToday}
            absentToday={stats.absentToday}
            attendanceRate={stats.attendanceRate}
            loading={loading}
          />
        </div>

        {/* Charts and Activities */}
        <div className="col-span-12 lg:col-span-8">
          <DepartmentChart
            departmentStats={stats.departmentStats}
            loading={loading}
          />
        </div>

        <div className="col-span-12 lg:col-span-4">
          <RecentActivities
            activities={stats.recentActivities}
            loading={loading}
          />
        </div>

        {/* Quick Actions */}
        <div className="col-span-12">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Quick Actions
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <button className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors group">
                <div className="text-blue-600 dark:text-blue-400 mb-2">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <div className="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                  Add Employee
                </div>
              </button>
              
              <button className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors group">
                <div className="text-green-600 dark:text-green-400 mb-2">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div className="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-green-600 dark:group-hover:text-green-400">
                  Mark Attendance
                </div>
              </button>
              
              <button className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/30 transition-colors group">
                <div className="text-purple-600 dark:text-purple-400 mb-2">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div className="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-purple-600 dark:group-hover:text-purple-400">
                  View Reports
                </div>
              </button>
              
              <button className="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors group">
                <div className="text-amber-600 dark:text-amber-400 mb-2">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-amber-600 dark:group-hover:text-amber-400">
                  Schedule
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
