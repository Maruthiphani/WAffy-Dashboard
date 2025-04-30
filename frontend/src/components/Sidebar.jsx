import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";

const Sidebar = () => {
  const location = useLocation();
  const path = location.pathname;
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Check if screen is mobile size
  useEffect(() => {
    const checkIfMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    // Initial check
    checkIfMobile();
    
    // Add event listener for window resize
    window.addEventListener("resize", checkIfMobile);
    
    // Cleanup
    return () => window.removeEventListener("resize", checkIfMobile);
  }, []);

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [path]);

  const menuItems = [
    { name: "Dashboard", path: "/dashboard", icon: "📊" },
    // { name: "Downloads", path: "/downloads", icon: "📥" },
    { name: "Settings", path: "/settings", icon: "⚙️" }
  ];

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <>
      {/* Hamburger Menu Button (Mobile Only) */}
      {isMobile && (
        <button 
          onClick={toggleMobileMenu}
          className="fixed top-20 right-4 z-30 p-2 rounded-md bg-white shadow-md hover:bg-gray-100 focus:outline-none"
          aria-label="Toggle menu"
        >
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            className="h-6 w-6 text-gray-700" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            {isMobileMenuOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      )}
      
      {/* Sidebar - Desktop: always visible, Mobile: only when toggled */}
      <div 
        className={`${isMobile ? 'fixed left-0 top-16 z-20 transform transition-transform duration-300 ease-in-out' : 'w-64 fixed left-0 top-16'} 
                   ${isMobile && !isMobileMenuOpen ? '-translate-x-full' : 'translate-x-0'} 
                   bg-white shadow-md h-screen`}
      >
        {/* Close button inside sidebar (Mobile Only) */}
        {isMobile && isMobileMenuOpen && (
          <button 
            onClick={toggleMobileMenu}
            className="absolute top-4 right-4 p-2 rounded-full bg-gray-100 hover:bg-gray-200 focus:outline-none"
            aria-label="Close menu"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-5 w-5 text-gray-700" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
        
        {/* Logo and Title */}
        <div className="flex flex-col items-center justify-center py-2">
          <img src="/logo.png" alt="WAffy Logo" className="h-12 w-auto mb-1" />
          <span className="text-2xl font-bold text-pink-500 tracking-wide">WAffy</span>
        </div>
        <div className="py-4">
          <ul>
            {menuItems.map((item) => (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center px-6 py-3 text-gray-700 hover:bg-pink-50 hover:text-pink-500 transition-colors ${
                    path === item.path ? "bg-pink-50 text-pink-500 border-r-4 border-pink-500" : ""
                  }`}
                >
                  <span className="mr-3">{item.icon}</span>
                  <span className="font-medium">{item.name}</span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>
      
      {/* Overlay for mobile when sidebar is open */}
      {isMobile && isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-10"
          onClick={() => setIsMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}
    </>
  );
};

export default Sidebar;
