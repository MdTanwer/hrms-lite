import { useEffect, useRef, useState } from "react";

import { Link } from "react-router";
import { ThemeToggleButton } from "@/components/common/ThemeToggleButton";
import UserProfile from "@/components/common/UserProfile";
import { MoreDotsIcon, ChevronRightIcon } from "@/icons";
import { useSidebar } from "@/context/SidebarContext";

const AppHeader: React.FC = () => {
  const [isApplicationMenuOpen, setApplicationMenuOpen] = useState(false);
  const { isMobileOpen, toggleMobileSidebar } = useSidebar();

  const toggleApplicationMenu = () => {
    setApplicationMenuOpen(!isApplicationMenuOpen);
  };

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === "k") {
        event.preventDefault();
        inputRef.current?.focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  return (
    <header className="sticky top-0 flex w-full bg-white border-gray-200 z-[100] dark:border-gray-800 dark:bg-gray-900 lg:border-b">
      <div className="flex flex-col items-center justify-between grow lg:flex-row lg:px-6">
        <div className="flex items-center justify-between w-full gap-2 px-3 py-3 border-b border-gray-200 dark:border-gray-800 sm:gap-4 lg:justify-normal lg:border-b-0 lg:px-0 lg:py-4">
          {/* Mobile/Tablet: Toggle Button */}
          <button
            onClick={toggleMobileSidebar}
            className="flex items-center justify-center w-10 h-10 text-gray-700 rounded-lg hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 lg:hidden"
            aria-label="Toggle Sidebar"
          >
            <ChevronRightIcon className={`w-6 h-6 transition-transform ${isMobileOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Mobile/Tablet: Centered Logo */}
          <Link to="/" className="absolute left-1/2 transform -translate-x-1/2 lg:hidden">
            <img
              className="dark:hidden w-8 h-8"
              src="/image.png"
              alt="Logo"
            />
            <img
              className="hidden dark:block w-8 h-8"
              src="/image.png"
              alt="Logo"
            />
          </Link>

          {/* Mobile/Tablet: Menu Button */}
          <button
            onClick={toggleApplicationMenu}
            className="flex items-center justify-center w-10 h-10 text-gray-700 rounded-lg hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 lg:hidden ml-auto"
          >
            <MoreDotsIcon className="w-6 h-6" />
          </button>
        </div>
        <div
          className={`${
            isApplicationMenuOpen ? "flex" : "hidden"
          } items-center justify-between w-full gap-4 px-5 py-4 lg:flex shadow-theme-md lg:justify-end lg:px-0 lg:shadow-none`}
        >
          <div className="flex items-center gap-2 2xsm:gap-3">
            {/* <!-- Dark Mode Toggler --> */}
            <ThemeToggleButton />
            
          </div>
          {/* <!-- User Area --> */}
          <UserProfile />
        </div>
      </div>
    </header>
  );
};

export default AppHeader;
