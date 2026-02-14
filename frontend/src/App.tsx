import { BrowserRouter as Router, Routes, Route } from "react-router";
import AppLayout from "@/layout/AppLayout";
import { ScrollToTop } from "@/components/common/ScrollToTop";
import ErrorBoundary from "@/components/ui/ErrorBoundary";
import Home from "@/pages/Dashboard/Home";
import EmployeeManagement from "@/pages/EmployeeManagement/employeemanagement";
import AttendanceManagement from "@/pages/AttendanceManagement/attendancemanagement";
import NotFound from "@/pages/NotFound";

// Import new providers
import { QueryProvider } from "@/providers/QueryProvider";
import { Toaster } from "react-hot-toast";

export default function App() {
  return (
    <ErrorBoundary>
      {/* Toast notifications - place at the highest level */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
        }}
        containerStyle={{
          zIndex: 9999999,
        }}
      />
      
      <QueryProvider>
        <Router>
          <ScrollToTop />
          <Routes>
            {/* Dashboard Layout */}
            <Route element={<AppLayout />}>
              <Route index path="/" element={<Home />} />
              <Route path="/employees" element={<EmployeeManagement />} />
              <Route path="/attendance" element={<AttendanceManagement />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </Router>
      </QueryProvider>
    </ErrorBoundary>
  );
}
