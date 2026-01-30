
import PageMeta from "../../components/common/PageMeta";
import PageBreadCrumb from "../../components/common/PageBreadCrumb";

export default function Home() {
  return (
    <>
      <PageMeta
        title="React.js HRMS Dashboard | HRMS Lite - React.js HRMS Management System"
        description="This is React.js HRMS Dashboard page for HRMS Lite - React.js Tailwind CSS HRMS Management System"
      />
      <div className="grid grid-cols-12 gap-4 md:gap-6">
      

     <PageBreadCrumb pageTitle="Dashboard" />
      
      </div>
    </>
  );
}
