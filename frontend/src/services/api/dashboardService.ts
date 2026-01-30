import apiClient from '../axios';

export interface DashboardOverview {
  employees: {
    total: number;
    active: number;
    inactive: number;
    on_leave: number;
  };
  attendance: {
    today: {
      total: number;
      present: number;
      absent: number;
      attendance_rate: number;
    };
    this_month: {
      average_attendance_rate: number;
      total_working_days: number;
    };
  };
  departments: {
    total: number;
    breakdown: Record<string, number>;
  };
  recent_activities: Array<{
    id: string;
    employee_id: string;
    employee_name: string;
    department: string;
    date: string;
    status: string;
    marked_at: string;
  }>;
}

export interface AttendanceTrend {
  date: string;
  present: number;
  absent: number;
  attendance_rate: number;
}

export interface DepartmentStats {
  department: string;
  total_employees: number;
  active_employees: number;
  average_salary: number;
  attendance_rate: number;
}

class DashboardService {
  private endpoint = '/api/v1/dashboard';

  /**
   * Get overall dashboard overview
   */
  async getOverview(): Promise<DashboardOverview> {
    const response = await apiClient.get<DashboardOverview>(
      `${this.endpoint}/overview` 
    );
    return response.data;
  }

  /**
   * Get attendance trend for last N days
   */
  async getAttendanceTrend(days: number = 7): Promise<AttendanceTrend[]> {
    const response = await apiClient.get<AttendanceTrend[]>(
      `${this.endpoint}/attendance/trend`,
      { params: { days } }
    );
    return response.data;
  }

  /**
   * Get department statistics
   */
  async getDepartmentStats(): Promise<DepartmentStats[]> {
    const response = await apiClient.get<DepartmentStats[]>(
      `${this.endpoint}/department/stats` 
    );
    return response.data;
  }

  /**
   * Get top performers by attendance
   */
  async getTopPerformers(
    limit: number = 10,
    startDate?: string,
    endDate?: string
  ): Promise<any[]> {
    const response = await apiClient.get(
      `${this.endpoint}/top-performers`,
      { params: { limit, start_date: startDate, end_date: endDate } }
    );
    return response.data;
  }

  /**
   * Get dashboard alerts
   */
  async getAlerts(): Promise<any[]> {
    const response = await apiClient.get(`${this.endpoint}/alerts`);
    return response.data;
  }
}

// Export singleton instance
export const dashboardService = new DashboardService();

// Export type
export type DashboardServiceType = typeof dashboardService;
