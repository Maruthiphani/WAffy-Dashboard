import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useClerk } from "@clerk/clerk-react";

const Sidebar = () => {
  const location = useLocation();
  const path = location.pathname;
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const { signOut } = useClerk();
  const navigate = useNavigate();

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
      {/* Mobile Header with Hamburger Menu */}
      {isMobile && (
        <div className="fixed top-0 left-0 w-full flex items-center justify-between px-4 py-3 bg-white shadow-md z-50">
          <button 
            onClick={toggleMobileMenu}
            className="p-2 rounded-md text-gray-700 hover:bg-gray-100 focus:outline-none"
            aria-label="Toggle menu"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className="h-6 w-6" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          
          <span className="text-xl font-bold text-pink-500 tracking-wide">WAffy</span>
          
          <button
            onClick={() => {
              signOut();
              navigate('/');
            }}
            className="p-2 rounded-md text-gray-700 hover:bg-gray-100 focus:outline-none"
            aria-label="Logout"
          >
            <span className="text-md">Logout</span>
          </button>
        </div>
      )}
      
      {/* Desktop Sidebar - Always visible */}
      {!isMobile && (
        <div className="w-64 fixed left-0 top-10 z-30 bg-white shadow-md h-screen overflow-y-auto">
          {/* Logo and Title for Desktop */}
          <div className="flex flex-col items-center justify-center py-8 pt-12 relative z-10">
            <div className="bg-white p-2 rounded-full shadow-sm">
              <img src="/logo.png" alt="WAffy Logo" className="h-16 w-auto relative z-10" />
            </div>
            <span className="text-2xl font-bold text-pink-500 tracking-wide relative z-10 mt-4">WAffy</span>
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
      )}
      
      {/* Mobile Sidebar - Only visible when toggled */}
      {isMobile && (
        <>
          <div 
            className={`fixed left-0 top-10 z-40 w-64 transform transition-transform duration-300 ease-in-out 
                      ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'} 
                      bg-white shadow-md h-screen overflow-y-auto`}
          >
            
            {/* Logo and Title for Mobile Sidebar */}
            <div className="flex flex-col items-center justify-center py-6 mt-8">
              <img src="/logo.png" alt="WAffy Logo" className="h-12 w-auto mb-2" />
              <span className="text-2xl font-bold text-pink-500 tracking-wide">WAffy</span>
            </div>
            
            {/* Menu Items */}
            <div className="py-4">
              <ul>
                {menuItems.map((item) => (
                  <li key={item.path}>
                    <Link
                      to={item.path}
                      className={`flex items-center px-6 py-3 text-gray-700 hover:bg-pink-50 hover:text-pink-500 transition-colors ${
                        path === item.path ? "bg-pink-50 text-pink-500 border-r-4 border-pink-500" : ""
                      }`}
                      onClick={toggleMobileMenu}
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
          {isMobileMenuOpen && (
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 z-30"
              onClick={toggleMobileMenu}
              aria-hidden="true"
            />
          )}
        </>
      )}
    </>
  );
};

export default Sidebar;
