import { BrowserRouter as Router, Routes, Route } from "react-router";
import AppLayout from "./layout/AppLayout";
import { ScrollToTop } from "./components/common/ScrollToTop";
import Home from "./pages/Dashboard/Home";
import EmployeeManagement from "./pages/EmployeeManagement/employeemanagement";

export default function App() {
  return (
    <>
      <Router>
        <ScrollToTop />
        <Routes>
          {/* Dashboard Layout */}
          <Route element={<AppLayout />}>
            <Route index path="/" element={<Home />} />
            <Route path="/employees" element={<EmployeeManagement />} />
            {/* <Route path="/basic-tables" element={<BasicTables />} /> */}
          </Route>
        </Routes>
      </Router>
    </>
  );
}
