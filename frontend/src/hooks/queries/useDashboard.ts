import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '@/services/api';

// Query keys
export const dashboardKeys = {
  all: ['dashboard'] as const,
  overview: () => [...dashboardKeys.all, 'overview'] as const,
  trend: (days: number) => [...dashboardKeys.all, 'trend', days] as const,
  departmentStats: () => [...dashboardKeys.all, 'department-stats'] as const,
  topPerformers: (limit: number, startDate?: string, endDate?: string) =>
    [...dashboardKeys.all, 'top-performers', limit, startDate, endDate] as const,
  alerts: () => [...dashboardKeys.all, 'alerts'] as const,
};

/**
 * Hook to fetch dashboard overview
 */
export const useDashboardOverview = () => {
  return useQuery({
    queryKey: dashboardKeys.overview(),
    queryFn: () => dashboardService.getOverview(),
    staleTime: 1000 * 60 * 2, // Refresh every 2 minutes
    refetchInterval: 1000 * 60 * 5, // Auto-refetch every 5 minutes
  });
};

/**
 * Hook to fetch attendance trend
 */
export const useAttendanceTrend = (days: number = 7) => {
  return useQuery({
    queryKey: dashboardKeys.trend(days),
    queryFn: () => dashboardService.getAttendanceTrend(days),
    staleTime: 1000 * 60 * 5,
  });
};

/**
 * Hook to fetch department statistics
 */
export const useDepartmentStats = () => {
  return useQuery({
    queryKey: dashboardKeys.departmentStats(),
    queryFn: () => dashboardService.getDepartmentStats(),
    staleTime: 1000 * 60 * 10, // Stats don't change frequently
  });
};

/**
 * Hook to fetch top performers
 */
export const useTopPerformers = (
  limit: number = 10,
  startDate?: string,
  endDate?: string
) => {
  return useQuery({
    queryKey: dashboardKeys.topPerformers(limit, startDate, endDate),
    queryFn: () => dashboardService.getTopPerformers(limit, startDate, endDate),
    staleTime: 1000 * 60 * 5,
  });
};

/**
 * Hook to fetch dashboard alerts
 */
export const useDashboardAlerts = () => {
  return useQuery({
    queryKey: dashboardKeys.alerts(),
    queryFn: () => dashboardService.getAlerts(),
    staleTime: 1000 * 60 * 2,
    refetchInterval: 1000 * 60 * 5, // Check for new alerts every 5 minutes
  });
};
