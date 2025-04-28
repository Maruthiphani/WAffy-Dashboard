import React, { useState, useEffect } from "react";
import DashboardHeader from "../components/DashboardHeader";
import { getOrders, getCustomers, getEnquiries, getIssues } from "../services/userService";
import { Table, Button, Tag } from "antd";
import { useUser } from "@clerk/clerk-react";

const Dashboard = () => {
  const [tab, setTab] = useState("orders");
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [enquiries, setEnquiries] = useState([]);
  const [issues, setIssues] = useState([]);

  const [customerFilter, setCustomerFilter] = useState("");
  const [dateFilter, setDateFilter] = useState(new Date().toISOString().split("T")[0]);

  const [selectedCustomer, setSelectedCustomer] = useState("");
  const [selectedDate, setSelectedDate] = useState("");

  // Use Clerk's useUser hook to get the authenticated user
  const { user: clerkUser, isLoaded: isClerkLoaded } = useUser();

  const handleLogout = () => alert("Logged out!");
  const handleUpdateProfile = () => alert("Update profile clicked!");

  useEffect(() => {
    // Fetch data when Clerk user is loaded
    if (isClerkLoaded) {
      fetchAllData();
    }
  }, [isClerkLoaded, clerkUser]);

  const fetchAllData = async () => {
    // Only fetch data if Clerk user is loaded
    if (!isClerkLoaded || !clerkUser) return;
    
    // Get the clerk_id to filter data by user
    const clerkId = clerkUser.id;
    
    try {
      const [ordersData, customersData, enquiriesData, issuesData] = await Promise.all([
        getOrders(clerkId),
        getCustomers(clerkId),
        getEnquiries(clerkId),
        getIssues(clerkId)
      ]);
      setOrders(ordersData);
      setCustomers(customersData);
      setEnquiries(enquiriesData);
      setIssues(issuesData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const handleFilterSubmit = () => {
    setSelectedCustomer(customerFilter);
    setSelectedDate(dateFilter);
  };

  const handleResetFilters = () => {
    // Reset all filters
    setCustomerFilter("");
    setDateFilter("");
    setSelectedCustomer("");
    setSelectedDate("");
  };

  const applyFilters = (item, idField = 'CustomerId', dateField = 'DeliveryDate') => {
    if (!item) return false;
    let itemCustomerId = item[idField];
    if (!itemCustomerId && idField === 'CustomerId') {
      itemCustomerId = item.customer_id;
    }
    
    const matchCustomer = !selectedCustomer || String(itemCustomerId) === String(selectedCustomer);
    
    let itemDate = item[dateField];
    if (!itemDate) {
      itemDate = item.created_at || item.UpdatedDate || item.CreatedDate;
    }
    
    // Convert date to YYYY-MM-DD format for comparison
    let formattedDate = '';
    if (itemDate && typeof itemDate === 'string') {
      formattedDate = itemDate.split('T')[0];
    }
    
    const matchDate = !selectedDate || formattedDate === selectedDate;
    
    return matchCustomer && matchDate;
  };

  // Apply filters to each data type
  const filteredOrders = orders.filter(order => applyFilters(order, 'customer_id', 'DeliveryDate'));
  const filteredCustomers = customers.filter(customer => applyFilters(customer, 'CustomerId', 'DeliveryDate'));
  const filteredEnquiries = enquiries.filter(enquiry => applyFilters(enquiry, 'CustomerId', 'DeliveryDate'));
  const filteredIssues = issues.filter(issue => applyFilters(issue, 'CustomerId', 'DeliveryDate'));

  const orderColumns = [
    { title: "Customer Name", dataIndex: "CustomerName", key: "CustomerName" },
    { title: "Order Number", dataIndex: "OrderNumber", key: "OrderNumber" },
    { title: "Item", dataIndex: "Item", key: "Item" },
    { title: "Quantity", dataIndex: "Quantity", key: "Quantity" },
    { title: "Notes", dataIndex: "Notes", key: "Notes" },
    { title: "Status", dataIndex: "Status", key: "Status", render: (text) => <Tag color="green">{text}</Tag> },
    { title: "Amount ($)", dataIndex: "Amount", key: "Amount" },
    { title: "Delivery Date", dataIndex: "DeliveryDate", key: "DeliveryDate" },
    { title: "Action", key: "action", render: () => <Button size="small" type="primary">Done</Button> }
  ];

  const customerColumns = [
    { title: "Customer ID", dataIndex: "CustomerId", key: "CustomerId" },
    { title: "Customer Name", dataIndex: "CustomerName", key: "CustomerName" },
    { title: "Email", dataIndex: "Email", key: "Email" },
    { title: "Delivery Date", dataIndex: "DeliveryDate", key: "DeliveryDate" },
    { title: "Updated Date", dataIndex: "UpdatedDate", key: "UpdatedDate" }
  ];

  const issueColumns = [
    { title: "Issue ID", dataIndex: "IssueId", key: "IssueId" },
    { title: "Customer ID", dataIndex: "CustomerId", key: "CustomerId" },
    // { title: "Order ID", dataIndex: "OrderId", key: "OrderId" },
    { title: "Issue Type", dataIndex: "IssueType", key: "IssueType" },
    { title: "Description", dataIndex: "Description", key: "Description" },
    { 
      title: "Priority", 
      dataIndex: "Priority", 
      key: "Priority",
      render: (priority) => {
        if (!priority) return null;
        let color = "blue";
        if (priority.toLowerCase() === "high") color = "red";
        else if (priority.toLowerCase() === "medium") color = "orange";
        else if (priority.toLowerCase() === "low") color = "green";
        return <Tag color={color}>{priority.toUpperCase()}</Tag>;
      }
    },
    { title: "Status", dataIndex: "Status", key: "Status" },
    // { title: "Resolution Notes", dataIndex: "ResolutionNotes", key: "ResolutionNotes" },
    { title: "Created Date", dataIndex: "DeliveryDate", key: "DeliveryDate", render: (date) => date ? new Date(date).toLocaleDateString() : "" },
    { title: "Updated Date", dataIndex: "UpdatedDate", key: "UpdatedDate", render: (date) => date ? new Date(date).toLocaleDateString() : "" },
  ];

  const enquiryColumns = [
    { title: "Enquiry ID", dataIndex: "EnquiryId", key: "EnquiryId" },
    { title: "Customer ID", dataIndex: "CustomerId", key: "CustomerId" },
    { title: "Description", dataIndex: "Description", key: "Description" },
    { title: "Category", dataIndex: "Category", key: "Category" },
    { 
      title: "Priority", 
      dataIndex: "Priority", 
      key: "Priority",
      render: (priority) => {
        if (!priority) return null;
        let color = "blue";
        if (priority.toLowerCase() === "high") color = "red";
        else if (priority.toLowerCase() === "medium") color = "orange";
        else if (priority.toLowerCase() === "low") color = "green";
        return <Tag color={color}>{priority.toUpperCase()}</Tag>;
      }
    },
    { title: "Status", dataIndex: "Status", key: "Status" },
    { title: "Follow Up Date", dataIndex: "FollowUpDate", key: "FollowUpDate", render: (date) => date ? new Date(date).toLocaleDateString() : "" },
    { title: "Delivery Date", dataIndex: "DeliveryDate", key: "DeliveryDate", render: (date) => date ? new Date(date).toLocaleDateString() : "" },
    { title: "Updated Date", dataIndex: "UpdatedDate", key: "UpdatedDate", render: (date) => date ? new Date(date).toLocaleDateString() : "" },
  ];

  const getCurrentData = () => {
    if (tab === "orders") return filteredOrders.map((item, index) => ({ ...item, key: index }));
    if (tab === "customers") return filteredCustomers.map((item, index) => ({ ...item, key: index }));
    if (tab === "enquiries") return filteredEnquiries.map((item, index) => ({ ...item, key: index }));
    if (tab === "issues") return filteredIssues.map((item, index) => ({ ...item, key: index }));
  };

  const getCurrentColumns = () => {
    if (tab === "orders") return orderColumns;
    if (tab === "customers") return customerColumns;
    if (tab === "enquiries") return enquiryColumns;
    if (tab === "issues") return issueColumns;
  };

  const getCustomerOptions = () => {
    let customerIds = [];
    
    // Collect customer IDs from all data types
    orders.forEach(order => {
      const id = order.customer_id || order.CustomerId;
      if (id) customerIds.push(id);
    });
    
    customers.forEach(customer => {
      const id = customer.CustomerId || customer.customer_id;
      if (id) customerIds.push(id);
    });
    
    enquiries.forEach(enquiry => {
      const id = enquiry.CustomerId || enquiry.customer_id;
      if (id) customerIds.push(id);
    });
    
    issues.forEach(issue => {
      const id = issue.CustomerId || issue.customer_id;
      if (id) customerIds.push(id);
    });
    
    // Remove duplicates and filter out empty values
    return [...new Set(customerIds)].filter(id => id);
  };

  const stats = {
    total: orders.length,
    responseRate: "87%",
    avgResponseTime: "28 min"
  };

  return (
    <>
      <DashboardHeader user={clerkUser} onLogout={handleLogout} onUpdateProfile={handleUpdateProfile} />
      <div className="min-h-screen bg-gray-50 space-y-6 pt-24 px-4 sm:px-6"> {/* Increased padding and added background */}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h3 className="text-sm font-medium text-gray-500">Total Orders</h3>
          <p className="text-2xl font-bold">{stats.total}</p>
        </div>
        
        {/* Priority Breakdown */}
        {/* <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-4">Priority Breakdown</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-red-600">Emergency</span>
                <span className="text-sm font-medium text-gray-700">{emergencyPercent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-red-500 h-2 rounded-full" style={{ width: `${emergencyPercent}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-orange-600">Important</span>
                <span className="text-sm font-medium text-gray-700">{importantPercent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-orange-500 h-2 rounded-full" style={{ width: `${importantPercent}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between mb-1">
                <span className="text-sm font-medium text-green-600">Routine</span>
                <span className="text-sm font-medium text-gray-700">{routinePercent}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: `${routinePercent}%` }}></div>
              </div>
            </div>
          </div>
        </div> */}
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h3 className="text-sm font-medium text-gray-500">Avg. Response Time</h3>
          <p className="text-2xl font-bold">{stats.avgResponseTime}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6">
        { ["orders", "customers", "enquiries", "issues"].map((tabName) => (
          <button
            key={tabName}
            onClick={() => setTab(tabName)}
            className={`px-6 py-2 rounded-full font-semibold shadow-md text-white bg-gradient-to-r from-pink-400 to-orange-400 hover:from-orange-400 hover:to-pink-400 transition duration-300 ${tab === tabName ? "border-4 border-yellow-300 scale-105" : "border-none"}`}
          >
            {tabName.charAt(0).toUpperCase() + tabName.slice(1)}
          </button>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6 items-end">
        <div className="flex flex-col">
          <label className="text-sm font-semibold mb-1">Customer ID:</label>
          <select
            className="p-2 border rounded w-48"
            value={customerFilter}
            onChange={(e) => setCustomerFilter(e.target.value)}
          >
            <option value="">All Customers</option>
            {getCustomerOptions().map((customerId) => (
              <option key={customerId} value={customerId}>{customerId}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col">
          <label className="text-sm font-semibold mb-1">Date:</label>
          <input
            type="date"
            className="p-2 border rounded w-48"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
          />
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleFilterSubmit}
            className="px-6 py-2 rounded-full font-semibold shadow-md text-white bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-400 transition duration-300"
          >
            Apply Filters
          </button>
          <button
            onClick={handleResetFilters}
            className="px-6 py-2 rounded-full font-semibold shadow-md text-white bg-gradient-to-r from-gray-400 to-gray-500 hover:from-gray-500 hover:to-gray-400 transition duration-300"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Table */}
      <Table
        columns={getCurrentColumns()}
        dataSource={getCurrentData()}
        pagination={{ pageSize: 10 }}
      />
      </div>
    </>
  );
};

export default Dashboard;
