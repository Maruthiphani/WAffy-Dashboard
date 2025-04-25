import React, { useState } from "react";

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
      format: "CSV",
      records: 98,
      size: "1.1 MB",
      url: "#"
    }
  ]);

  const handleFormatChange = (e) => {
    setSelectedFormat(e.target.value);
  };

  const handleDateChange = (e) => {
    const { name, value } = e.target;
    setDateRange({
      ...dateRange,
      [name]: value
    });
  };

  const handleIncludeOptionChange = (e) => {
    const { name, checked } = e.target;
    setIncludeOptions({
      ...includeOptions,
      [name]: checked
    });
  };

  const handleDownload = (e) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate download process
    setTimeout(() => {
      const newDownload = {
        id: downloadHistory.length + 1,
        date: new Date().toISOString().split("T")[0],
        format: selectedFormat === "excel" ? "Excel" : "CSV",
        records: Math.floor(Math.random() * 100) + 50,
        size: `${(Math.random() * 3 + 0.5).toFixed(1)} MB`,
        url: "#"
      };
      
      setDownloadHistory([newDownload, ...downloadHistory]);
      setLoading(false);
      
      // Show success message or trigger actual download
      alert("Download prepared successfully!");
    }, 2000);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Downloads</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Download Form */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-4">Export Data</h2>
          
          <form onSubmit={handleDownload}>
            {/* Format Selection */}
            <div className="mb-4">
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
                    className="text-pink-500"
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
                    className="text-pink-500"
                  />
                  <span className="ml-2">CSV</span>
                </label>
              </div>
            </div>
            
            {/* Date Range */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date Range
              </label>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">From</label>
                  <input
                    type="date"
                    name="startDate"
                    value={dateRange.startDate}
                    onChange={handleDateChange}
                    className="w-full p-2 border rounded focus:ring-pink-500 focus:border-pink-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">To</label>
                  <input
                    type="date"
                    name="endDate"
                    value={dateRange.endDate}
                    onChange={handleDateChange}
                    className="w-full p-2 border rounded focus:ring-pink-500 focus:border-pink-500"
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
                    className="text-pink-500"
                  />
                  <span className="ml-2 text-sm">Customer Information</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="messageContent"
                    checked={includeOptions.messageContent}
                    onChange={handleIncludeOptionChange}
                    className="text-pink-500"
                  />
                  <span className="ml-2 text-sm">Message Content</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="responseData"
                    checked={includeOptions.responseData}
                    onChange={handleIncludeOptionChange}
                    className="text-pink-500"
                  />
                  <span className="ml-2 text-sm">Response Data</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="categories"
                    checked={includeOptions.categories}
                    onChange={handleIncludeOptionChange}
                    className="text-pink-500"
                  />
                  <span className="ml-2 text-sm">Categories & Tags</span>
                </label>
              </div>
            </div>
            
            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className={`w-full px-4 py-2 bg-gradient-to-r from-pink-500 to-yellow-400 text-white rounded-md shadow-md hover:shadow-lg transition ${
                loading ? "opacity-70 cursor-not-allowed" : ""
              }`}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Preparing Download...
                </span>
              ) : (
                "Generate Export"
              )}
            </button>
          </form>
        </div>
        
        {/* Download History */}
        <div className="lg:col-span-3 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-4">Download History</h2>
          
          {downloadHistory.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Format</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Records</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Size</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {downloadHistory.map((item) => (
                    <tr key={item.id}>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{item.date}</td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{item.format}</td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{item.records}</td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{item.size}</td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm">
                        <a 
                          href={item.url} 
                          className="text-pink-500 hover:text-pink-700"
                          download
                        >
                          Download
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-gray-500 text-center py-4">No download history available</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Downloads;
