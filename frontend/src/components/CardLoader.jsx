import React from 'react';

/**
 * CardLoader component for displaying skeleton loading state for statistic cards
 * @param {Object} props - Component props
 * @param {number} props.count - Number of skeleton cards to display
 * @param {string} props.className - Additional CSS classes
 */
const CardLoader = ({ 
  count = 4, 
  className = '' 
}) => {
  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
      {Array(count).fill().map((_, index) => (
        <div 
          key={`card-${index}`} 
          className="bg-white rounded-lg shadow-md p-4 overflow-hidden"
        >
          {/* Card title */}
          <div className="h-5 bg-gray-200 rounded w-2/3 mb-4 animate-pulse"></div>
          
          {/* Card value */}
          <div 
            className="h-8 bg-gray-200 rounded w-1/2 mb-3 animate-pulse"
            style={{ animationDelay: `${index * 0.1}s` }}
          ></div>
          
          {/* Card subtitle */}
          <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse"></div>
          
          {/* Card footer */}
          <div className="mt-4 pt-4 border-t">
            <div className="h-4 bg-gray-200 rounded w-full animate-pulse"></div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CardLoader;
