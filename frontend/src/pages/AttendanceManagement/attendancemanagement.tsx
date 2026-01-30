import { useState } from 'react';
import PageMeta from "../../components/common/PageMeta";
import PageBreadCrumb from "../../components/common/PageBreadCrumb";
import Button from "../../components/ui/Button";
import AttendanceForm from "../../components/attendance/AttendanceForm";
import AttendanceStats from "../../components/attendance/AttendanceStats";
import AttendanceTable from "../../components/attendance/AttendanceTable";
import Modal from "../../components/Modal/Modal";
import Alert from "../../components/ui/Alert";
import { useAttendance } from "../../hooks/useAttendance";
import { AttendanceFormData } from "../../schemas/attendanceSchema";

export default function AttendanceManagement() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { attendances, employees, addAttendance, getAttendanceStats, loading, error, clearError } = useAttendance();
  const stats = getAttendanceStats();

  const handleFormSubmit = async (data: AttendanceFormData) => {
    const success = await addAttendance(data);
    if (success) {
      setIsModalOpen(false);
    }
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    clearError();
  };

  return (
    <>
      <PageMeta
        title="Attendance Management | HRMS Lite"
        description="Mark and manage employee attendance records"
      />
      <PageBreadCrumb pageTitle="Attendance Management" />
      
      {error && (
        <div className="mb-6">
          <Alert type="error" dismissible onDismiss={clearError}>
            {error}
          </Alert>
        </div>
      )}
      
      <div className="grid grid-cols-12 gap-4 md:gap-6">
        <div className="col-span-12">
          <div className="rounded-lg border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-800 dark:shadow-gray-900/10">
            <div className="border-b border-gray-200 p-6 dark:border-gray-700">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-100">Attendance Management</h2>
                <Button onClick={() => setIsModalOpen(true)} disabled={loading}>
                  {loading ? 'Processing...' : 'Mark Attendance'}
                </Button>
              </div>
              
              <div className="mt-6">
                <AttendanceStats {...stats} loading={loading} />
              </div>
            </div>
            
            <div className="p-6">
              <AttendanceTable 
                attendances={attendances} 
                loading={loading}
                emptyAction={
                  <Button onClick={() => setIsModalOpen(true)}>
                    Mark First Attendance
                  </Button>
                }
              />
            </div>
          </div>
        </div>
      </div>
      
      <Modal
        isOpen={isModalOpen}
        onClose={handleModalClose}
        title="Mark Attendance"
        size="lg"
      >
        <AttendanceForm
          onSubmit={handleFormSubmit}
          onCancel={handleModalClose}
          employees={employees}
        />
      </Modal>
    </>
  );
}
