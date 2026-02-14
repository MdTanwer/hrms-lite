export interface AttendanceDetailsStatsProps {
  totalLeave: number;
  totalAbsent: number;
  workingDays: number;
  presentDays: number;
  halfDays?: number;
  /** When provided (e.g. from API), used instead of computing from presentDays/halfDays/workingDays */
  attendanceRate?: number;
}

const baseCardClass = 'rounded-lg border p-2 min-w-0 flex flex-col items-center justify-center text-center';

function getAttendanceRateColor(rate: number): string {
  if (rate >= 80) return 'text-emerald-600 dark:text-emerald-400';
  if (rate >= 50) return 'text-amber-600 dark:text-amber-400';
  return 'text-red-600 dark:text-red-400';
}

function getAttendanceRateBgBorder(rate: number): string {
  if (rate >= 80)
    return 'border-emerald-200 bg-emerald-50/80 dark:border-emerald-800 dark:bg-emerald-900/20';
  if (rate >= 50)
    return 'border-amber-200 bg-amber-50/80 dark:border-amber-800 dark:bg-amber-900/20';
  return 'border-red-200 bg-red-50/80 dark:border-red-800 dark:bg-red-900/20';
}

export default function AttendanceDetailsStats({
  totalLeave,
  totalAbsent,
  workingDays,
  presentDays,
  halfDays = 0,
  attendanceRate: attendanceRateFromApi,
}: AttendanceDetailsStatsProps) {
  const effectivePresent = presentDays + 0.5 * halfDays;
  const computedRate =
    workingDays > 0 ? Math.round((effectivePresent / workingDays) * 1000) / 10 : 0;
  const attendanceRate =
    attendanceRateFromApi != null && !Number.isNaN(attendanceRateFromApi)
      ? Number(attendanceRateFromApi)
      : computedRate;
  const displayRate = Number.isFinite(attendanceRate) ? attendanceRate : 0;

  return (
    <div className="grid grid-cols-6 gap-2 w-full min-w-0">
      {/* Present Days — green (positive) */}
      <div
        className={`${baseCardClass} border-emerald-200 bg-emerald-50/80 dark:border-emerald-800 dark:bg-emerald-900/20`}
      >
        <p className="text-[10px] font-semibold uppercase tracking-wide text-emerald-600 dark:text-emerald-400 truncate">
          Present
        </p>
        <p className="mt-0.5 text-lg font-bold text-emerald-900 dark:text-emerald-100 tabular-nums">
          {presentDays}
        </p>
      </div>

      {/* Total Leave — blue */}
      <div
        className={`${baseCardClass} border-blue-200 bg-blue-50/80 dark:border-blue-800 dark:bg-blue-900/20`}
      >
        <p className="text-[10px] font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-400 truncate">
          Leave
        </p>
        <p className="mt-0.5 text-lg font-bold text-blue-900 dark:text-blue-100 tabular-nums">
          {totalLeave}
        </p>
      </div>

      {/* Total Absent — red */}
      <div
        className={`${baseCardClass} border-red-200 bg-red-50/80 dark:border-red-800 dark:bg-red-900/20`}
      >
        <p className="text-[10px] font-semibold uppercase tracking-wide text-red-600 dark:text-red-400 truncate">
          Absent
        </p>
        <p className="mt-0.5 text-lg font-bold text-red-900 dark:text-red-100 tabular-nums">
          {totalAbsent}
        </p>
      </div>

      {/* Half Days — amber */}
      <div
        className={`${baseCardClass} border-amber-200 bg-amber-50/80 dark:border-amber-800 dark:bg-amber-900/20`}
      >
        <p className="text-[10px] font-semibold uppercase tracking-wide text-amber-600 dark:text-amber-400 truncate">
          Half
        </p>
        <p className="mt-0.5 text-lg font-bold text-amber-900 dark:text-amber-100 tabular-nums">
          {halfDays}
        </p>
      </div>

      {/* Working Days — neutral */}
      <div
        className={`${baseCardClass} border-slate-200 bg-slate-50/80 dark:border-slate-700 dark:bg-slate-800/50`}
      >
        <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400 truncate">
          Working
        </p>
        <p className="mt-0.5 text-lg font-bold text-slate-900 dark:text-slate-100 tabular-nums">
          {workingDays}
        </p>
      </div>

      {/* Attendance Rate — green / amber / red by value */}
      <div
        className={`${baseCardClass} ${getAttendanceRateBgBorder(displayRate)}`}
      >
        <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-600 dark:text-slate-400 truncate">
          Rate
        </p>
        <p
          className={`mt-0.5 text-lg font-bold tabular-nums ${getAttendanceRateColor(displayRate)}`}
        >
          {displayRate}%
        </p>
      </div>
    </div>
  );
}
