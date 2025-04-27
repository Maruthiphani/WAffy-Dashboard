import React, { useState, useEffect } from "react";
import DashboardHeader from "../components/DashboardHeader";
import { getOrders, getCustomers, getEnquiries } from "../services/userService";
import { Table, Button, Tag } from "antd";

const Dashboard = () => {
  const [tab, setTab] = useState("orders"); // 'orders', 'customers', 'enquiries'
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [enquiries, setEnquiries] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState("");
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]);

  const [user] = useState({
    firstName: "Jane",
    lastName: "Doe",
    email: "jane.doe@example.com",
    profileImage: ""
  });

  const handleLogout = () => alert("Logged out!");
  const handleUpdateProfile = () => alert("Update profile clicked!");

  useEffect(() => {
    const fetchAllData = async () => {
      const [ordersData, customersData, enquiriesData] = await Promise.all([
        getOrders(),
        getCustomers(),
        getEnquiries()
      ]);
      setOrders(ordersData);
      setCustomers(customersData);
      setEnquiries(enquiriesData);
    };
    fetchAllData();
  }, []);



  const filteredOrders = orders.filter(order => {
    const matchCustomer = selectedCustomer ? order.customer_id === selectedCustomer : true;
    const matchDate = selectedDate ? order.DeliveryDate?.split("T")[0] === selectedDate : true;
    return matchCustomer && matchDate;
  });

  const filteredCustomers = customers.filter(customer => {
    const matchCustomer = selectedCustomer ? customer.CustomerId === selectedCustomer : true;
    const matchDate = selectedDate ? customer.DeliveryDate?.split("T")[0] === selectedDate : true;
    return matchCustomer && matchDate;
  });

  const filteredEnquiries = enquiries.filter(enquiry => {
    const matchCustomer = selectedCustomer ? enquiry.CustomerId === selectedCustomer : true;
    const matchDate = selectedDate ? enquiry.DeliveryDate?.split("T")[0] === selectedDate : true;
    return matchCustomer && matchDate;
  });

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
  };

  const getCurrentColumns = () => {
    if (tab === "orders") return orderColumns;
    if (tab === "customers") return customerColumns;
    if (tab === "enquiries") return enquiryColumns;
  };

  const getCustomerOptions = () => {
    if (tab === "orders") return [...new Set(orders.map(order => order.customer_id))];
    if (tab === "customers") return [...new Set(customers.map(customer => customer.CustomerId))];
    if (tab === "enquiries") return [...new Set(enquiries.map(enquiry => enquiry.CustomerId))];
    return [];
  };

  const columns = [
    { title: 'Customer Name', dataIndex: 'CustomerName', key: 'CustomerName' },
    { title: 'Order Number', dataIndex: 'OrderNumber', key: 'OrderNumber' },
    { title: 'Item', dataIndex: 'Item', key: 'Item' },
    { title: 'Quantity', dataIndex: 'Quantity', key: 'Quantity' },
    { title: 'Notes', dataIndex: 'Notes', key: 'Notes' },
    { 
      title: 'Status', 
      dataIndex: 'Status', 
      key: 'Status',
      render: (status) => (
        <Tag color={status === 'Pending' ? 'volcano' : 'green'}>
          {status?.toUpperCase()}
        </Tag>
      ),
    },
    { 
      title: 'Amount ($)', 
      dataIndex: 'Amount', 
      key: 'Amount',
      render: (amount) => `$${amount?.toFixed(2)}`,
    },
    { 
      title: 'Delivery Date', 
      dataIndex: 'DeliveryDate', 
      key: 'DeliveryDate',
      render: (date) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_, record) => (
        <Button type="primary" size="small">
          Done
        </Button>
      ),
    },
  ];

  const stats = {
    total: orders.length,
    responseRate: "87%", // Placeholder
    avgResponseTime: "28 min" // Placeholder
  };

  return (
    <div className="space-y-6">
      <DashboardHeader user={user} onLogout={handleLogout} onUpdateProfile={handleUpdateProfile} />

       {/* 🌟 Stats Cards */}
       <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h3 className="text-sm font-medium text-gray-500">Total Orders</h3>
          <p className="text-2xl font-bold">{stats.total}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h3 className="text-sm font-medium text-gray-500">Response Rate</h3>
          <p className="text-2xl font-bold">{stats.responseRate}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h3 className="text-sm font-medium text-gray-500">Avg. Response Time</h3>
          <p className="text-2xl font-bold">{stats.avgResponseTime}</p>
        </div>
      </div>


      {/* Tabs */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={() => setTab("orders")}
          className={`px-4 py-2 rounded ${tab === "orders" ? "bg-blue-600 text-white" : "bg-gray-300 text-gray-800"}`}
        >
          Orders
        </button>
        <button
          onClick={() => setTab("customers")}
          className={`px-4 py-2 rounded ${tab === "customers" ? "bg-blue-600 text-white" : "bg-gray-300 text-gray-800"}`}
        >
          Customers
        </button>
        <button
          onClick={() => setTab("enquiries")}
          className={`px-4 py-2 rounded ${tab === "enquiries" ? "bg-blue-600 text-white" : "bg-gray-300 text-gray-800"}`}
        >
          Enquiries
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <select
          className="p-2 border rounded"
          value={selectedCustomer}
          onChange={(e) => setSelectedCustomer(e.target.value)}
        >
          <option value="">All Customers</option>
          {getCustomerOptions().map((customerId) => (
            <option key={customerId} value={customerId}>{customerId}</option>
          ))}
        </select>

        <input
          type="date"
          className="p-2 border rounded"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />
      </div>

      {/* Table */}
      <Table
        columns={getCurrentColumns()}
        dataSource={getCurrentData()}
        pagination={{ pageSize: 10 }}
      />
    </div>
  );
};

export default Dashboard;
