import React, { useState } from "react";
import { SignedIn } from "@clerk/clerk-react";
import DashboardHeader from "../components/DashboardHeader";

const Downloads = () => {
  const [selectedFormat, setSelectedFormat] = useState("excel");
  const [dateRange, setDateRange] = useState({
    startDate: "",
    endDate: ""
  });
  const [includeOptions, setIncludeOptions] = useState({
    customerInfo: true,
    messageContent: true,
    responseData: true,
    categories: true
  });
  const [loading, setLoading] = useState(false);
  const [downloadHistory, setDownloadHistory] = useState([
    {
      id: 1,
      date: "2025-04-15",
      format: "Excel",
      records: 156,
      size: "2.3 MB",
      url: "#"
    },
    {
      id: 2,
      date: "2025-04-01",
      format: "Excel",
      records: 98,
      size: "1.7 MB",
      url: "#"
    },
    {
      id: 3,
      date: "2025-03-15",
      format: "CSV",
      records: 120,
      size: "1.9 MB",
      url: "#"
    }
  ]);

  const handleFormatChange = (e) => {
    setSelectedFormat(e.target.value);
  };

  const handleDateChange = (e) => {
    setDateRange({
      ...dateRange,
      [e.target.name]: e.target.value
    });
  };

  const handleIncludeOptionChange = (e) => {
    setIncludeOptions({
      ...includeOptions,
      [e.target.name]: e.target.checked
    });
  };

  const handleDownload = () => {
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      alert("Download initiated!");
      
      // Add to history (in a real app, this would come from the API)
      const newDownload = {
        id: downloadHistory.length + 1,
        date: new Date().toISOString().split('T')[0],
        format: selectedFormat === 'excel' ? 'Excel' : 'CSV',
        records: Math.floor(Math.random() * 100) + 50,
        size: (Math.random() * 3 + 1).toFixed(1) + " MB",
        url: "#"
      };
      
      setDownloadHistory([newDownload, ...downloadHistory]);
    }, 1500);
  };

  return (
    <>
      <SignedIn>
        <DashboardHeader />
      </SignedIn>
      
      {/* Main content with top padding to account for fixed header */}
      <div className="pt-20 px-6 max-w-screen-2xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Export Options */}
          <div className="lg:col-span-1">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-6">Export Data</h2>
              
              {/* Format Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Export Format
                </label>
                <div className="flex space-x-4">
                  <label className="inline-flex items-center">
                    <input
                      type="radio"
                      name="format"
                      value="excel"
                      checked={selectedFormat === "excel"}
                      onChange={handleFormatChange}
                      className="h-4 w-4 text-pink-600"
                    />
                    <span className="ml-2">Excel</span>
                  </label>
                  <label className="inline-flex items-center">
                    <input
                      type="radio"
                      name="format"
                      value="csv"
                      checked={selectedFormat === "csv"}
                      onChange={handleFormatChange}
                      className="h-4 w-4 text-pink-600"
                    />
                    <span className="ml-2">CSV</span>
                  </label>
                </div>
              </div>
              
              {/* Date Range */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date Range
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">
                      Start Date
                    </label>
                    <input
                      type="date"
                      name="startDate"
                      value={dateRange.startDate}
                      onChange={handleDateChange}
                      className="w-full p-2 border border-gray-300 rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">
                      End Date
                    </label>
                    <input
                      type="date"
                      name="endDate"
                      value={dateRange.endDate}
                      onChange={handleDateChange}
                      className="w-full p-2 border border-gray-300 rounded"
                    />
                  </div>
                </div>
              </div>
              
              {/* Include Options */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Include in Export
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="customerInfo"
                      checked={includeOptions.customerInfo}
                      onChange={handleIncludeOptionChange}
                      className="h-4 w-4 text-pink-600"
                    />
                    <span className="ml-2 text-sm">Customer Information</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="messageContent"
                      checked={includeOptions.messageContent}
                      onChange={handleIncludeOptionChange}
                      className="h-4 w-4 text-pink-600"
                    />
                    <span className="ml-2 text-sm">Message Content</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="responseData"
                      checked={includeOptions.responseData}
                      onChange={handleIncludeOptionChange}
                      className="h-4 w-4 text-pink-600"
                    />
                    <span className="ml-2 text-sm">Response Data</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      name="categories"
                      checked={includeOptions.categories}
                      onChange={handleIncludeOptionChange}
                      className="h-4 w-4 text-pink-600"
                    />
                    <span className="ml-2 text-sm">Categories</span>
                  </label>
                </div>
              </div>
              
              {/* Download Button */}
              <button
                onClick={handleDownload}
                disabled={loading}
                className="w-full py-2 px-4 bg-gradient-to-r from-pink-500 to-yellow-500 text-white rounded-md hover:from-pink-600 hover:to-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-pink-500 disabled:opacity-50"
              >
                {loading ? "Processing..." : "Download Data"}
              </button>
            </div>
          </div>
          
          {/* Download History */}
          <div className="lg:col-span-2">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-6">Download History</h2>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Format
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Records
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Size
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Action
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {downloadHistory.map((item) => (
                      <tr key={item.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.date}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.format}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.records}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {item.size}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <a href={item.url} className="text-pink-600 hover:text-pink-900">
                            Download
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              {downloadHistory.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No download history available
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Downloads;
