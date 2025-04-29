import React from 'react';

/**
 * Loader component for displaying loading states
 * @param {Object} props - Component props
 * @param {string} props.size - Size of the loader ('sm', 'md', 'lg')
 * @param {string} props.color - Color of the loader ('primary', 'secondary', 'white')
 * @param {string} props.text - Optional text to display below the loader
 * @param {boolean} props.fullPage - Whether to display the loader full page
 * @param {string} props.className - Additional CSS classes
 */
const Loader = ({ 
  size = 'md', 
  color = 'primary', 
  text = '', 
  fullPage = false,
  className = ''
}) => {
  // Size classes
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };
  
  // Color classes
  const colorClasses = {
    primary: 'text-pink-500',
    secondary: 'text-yellow-500',
    white: 'text-white',
  };
  
  // Container classes for full page
  const containerClasses = fullPage 
    ? 'fixed inset-0 flex flex-col items-center justify-center bg-white bg-opacity-80 z-50' 
    : 'flex flex-col items-center justify-center';
  
  return (
    <div className={`${containerClasses} ${className}`}>
      <svg 
        className={`animate-spin ${sizeClasses[size]} ${colorClasses[color]}`} 
        xmlns="http://www.w3.org/2000/svg" 
        fill="none" 
        viewBox="0 0 24 24"
      >
        <circle 
          className="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          strokeWidth="4"
        ></circle>
        <path 
          className="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      {text && (
        <p className={`mt-2 text-sm font-medium ${colorClasses[color]}`}>
          {text}
        </p>
      )}
    </div>
  );
};

export default Loader;
