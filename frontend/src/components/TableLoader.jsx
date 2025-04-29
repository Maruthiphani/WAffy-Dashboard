import React from 'react';

/**
 * TableLoader component for displaying skeleton loading state for tables
 * @param {Object} props - Component props
 * @param {number} props.rows - Number of skeleton rows to display
 * @param {number} props.columns - Number of skeleton columns to display
 * @param {string} props.className - Additional CSS classes
 */
const TableLoader = ({ 
  rows = 5, 
  columns = 4, 
  className = '' 
}) => {
  return (
    <div className={`w-full overflow-hidden rounded-lg shadow-md ${className}`}>
      {/* Table header skeleton */}
      <div className="bg-gray-50 border-b">
        <div className="flex">
          {Array(columns).fill().map((_, i) => (
            <div 
              key={`header-${i}`} 
              className="flex-1 p-4"
            >
              <div className="h-6 bg-gray-200 rounded animate-pulse"></div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Table body skeleton */}
      <div className="bg-white">
        {Array(rows).fill().map((_, rowIndex) => (
          <div 
            key={`row-${rowIndex}`} 
            className="flex border-b last:border-b-0"
          >
            {Array(columns).fill().map((_, colIndex) => (
              <div 
                key={`cell-${rowIndex}-${colIndex}`} 
                className="flex-1 p-4"
              >
                <div 
                  className={`h-4 bg-gray-200 rounded animate-pulse ${
                    // Add different widths to make it look more natural
                    colIndex % 3 === 0 ? 'w-3/4' : 
                    colIndex % 3 === 1 ? 'w-1/2' : 'w-full'
                  }`}
                  style={{
                    // Add slight delay to each row for wave effect
                    animationDelay: `${rowIndex * 0.1}s`
                  }}
                ></div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TableLoader;
