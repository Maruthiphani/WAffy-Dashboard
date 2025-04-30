import React, { useState, useEffect } from "react";
import DashboardHeader from "../components/DashboardHeader";
import { getOrders, getCustomers, getEnquiries, getIssues, getResponseMetrics, getUserSettings, updateOrderStatus } from "../services/userService";
import SetupBanner from "../components/SetupBanner";
import ErrorBanner from "../components/ErrorBanner";
import { Table, Button, Tag, Progress, Dropdown } from "antd";
import { MoreOutlined } from "@ant-design/icons";
import { useUser } from "@clerk/clerk-react";
import Loader from "../components/Loader";
import TableLoader from "../components/TableLoader";
import CardLoader from "../components/CardLoader";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";

const Dashboard = () => {
  const [visibleData, setVisibleData] = useState([]);
  const [tab, setTab] = useState("orders");
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [enquiries, setEnquiries] = useState([]);
  const [issues, setIssues] = useState([]);
  const [responseMetrics, setResponseMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dataLoadingState, setDataLoadingState] = useState({
    orders: true,
    customers: true,
    enquiries: true,
    issues: true,
    metrics: true,
  });

  const [customerFilter, setCustomerFilter] = useState("");
  const [dateFilter, setDateFilter] = useState(new Date().toISOString().split("T")[0]);

  const [selectedCustomer, setSelectedCustomer] = useState("");
  
  // State for the setup banner
  const [showSetupBanner, setShowSetupBanner] = useState(false);
  const [settingsChecked, setSettingsChecked] = useState(false);
  const [selectedDate, setSelectedDate] = useState("");

  // Use Clerk's useUser hook to get the authenticated user
  const { user: clerkUser, isLoaded: isClerkLoaded } = useUser();

  const handleLogout = () => alert("Logged out!");
  const handleUpdateProfile = () => alert("Update profile clicked!");

  useEffect(() => {
    if (isClerkLoaded && clerkUser?.id) {
      fetchAllData();
      checkUserSettings();
    }
  }, [isClerkLoaded, clerkUser?.id, tab, customerFilter, dateFilter]);
  
  // Check if the user has configured their WhatsApp and CRM settings
  const checkUserSettings = async () => {
    if (!settingsChecked && clerkUser) {
      try {
        const settings = await getUserSettings(clerkUser.id);
        
        // Check if WhatsApp settings are configured
        const hasWhatsAppSettings = settings && 
          (settings.whatsapp_api_key && settings.whatsapp_phone_number_id && settings.whatsapp_app_id && settings.whatsapp_app_secret && settings.whatsapp_verify_token);
        
        // Check if CRM settings are configured (either HubSpot or Excel export)
        const hasCrmSettings = settings && 
          (settings.hubspot_access_token || settings.view_consolidated_data);
        
        // Show the banner if either WhatsApp or CRM settings are not configured
        setShowSetupBanner(!hasWhatsAppSettings || !hasCrmSettings);
        setSettingsChecked(true);
      } catch (error) {
        console.error('Error checking user settings:', error);
        // If there's an error, assume settings are not configured
        setShowSetupBanner(true);
        setSettingsChecked(true);
      }
    }
  };

  const fetchAllData = async () => {
    if (!isClerkLoaded || !clerkUser) return;

    setLoading(true);
    setDataLoadingState({
      orders: true,
      customers: true,
      enquiries: true,
      issues: true,
      metrics: true,
    });

    const clerkId = clerkUser.id;

    try {
      const fetchOrders = async () => {
        try {
          const data = await getOrders(clerkId);
          
          // Add random amounts within $20 range for each order
          const ordersWithRandomAmounts = data.map(order => ({
            ...order,
            Amount: order.Amount || (Math.floor(Math.random() * 20) + 1).toFixed(2) // Random amount between $1 and $20
          }));
          
          setOrders(ordersWithRandomAmounts);
          setDataLoadingState((prev) => ({ ...prev, orders: false }));
        } catch (error) {
          console.error("Error fetching orders:", error);
          setDataLoadingState((prev) => ({ ...prev, orders: false }));
        }
      };

      const fetchCustomers = async () => {
        try {
          const data = await getCustomers(clerkId);
          setCustomers(data);
          setDataLoadingState((prev) => ({ ...prev, customers: false }));
        } catch (error) {
          console.error("Error fetching customers:", error);
          setDataLoadingState((prev) => ({ ...prev, customers: false }));
        }
      };

      const fetchEnquiries = async () => {
        try {
          const data = await getEnquiries(clerkId);
          setEnquiries(data);
          setDataLoadingState((prev) => ({ ...prev, enquiries: false }));
        } catch (error) {
          console.error("Error fetching enquiries:", error);
          setDataLoadingState((prev) => ({ ...prev, enquiries: false }));
        }
      };

      const fetchIssues = async () => {
        try {
          const data = await getIssues(clerkId);
          setIssues(data);
          setDataLoadingState((prev) => ({ ...prev, issues: false }));
        } catch (error) {
          console.error("Error fetching issues:", error);
          setDataLoadingState((prev) => ({ ...prev, issues: false }));
        }
      };

      const fetchMetrics = async () => {
        try {
          const data = await getResponseMetrics(clerkId, 30);
          setResponseMetrics(data);
          setDataLoadingState((prev) => ({ ...prev, metrics: false }));
        } catch (error) {
          console.error("Error fetching metrics:", error);
          setDataLoadingState((prev) => ({ ...prev, metrics: false }));
        }
      };

      await Promise.all([fetchOrders(), fetchCustomers(), fetchEnquiries(), fetchIssues(), fetchMetrics()]);

      setLoading(false);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setLoading(false);
    }
  };

  // const handleFilterSubmit = () => {
  //   setSelectedCustomer(customerFilter);
  //   setSelectedDate(dateFilter);
  // };

  // const handleResetFilters = () => {
  //   setCustomerFilter("");
  //   setDateFilter("");
  //   setSelectedCustomer("");
  //   setSelectedDate("");
  // };

  const handleFilterSubmit = () => {
    if (!dateFilter) {
      alert("Please select a valid date before applying filters.");
      return;
    }
    setSelectedCustomer(customerFilter);
    setSelectedDate(dateFilter);
  };

  const handleResetFilters = () => {
    setCustomerFilter("");
    setDateFilter("");
    setSelectedCustomer("");
    setSelectedDate("");
  };


  const applyFilters = (item, idField = "CustomerId", dateField = "DeliveryDate") => {
    if (!item) return false;
    let itemCustomerId = item[idField];
    if (!itemCustomerId && idField === "CustomerId") {
      itemCustomerId = item.customer_id;
    }

    const matchCustomer = !selectedCustomer || String(itemCustomerId) === String(selectedCustomer);

    let itemDate = item[dateField];
    if (!itemDate) {
      itemDate = item.created_at || item.UpdatedDate || item.CreatedDate;
    }

    let formattedDate = "";
    if (itemDate && typeof itemDate === "string") {
      try {
        formattedDate = new Date(itemDate).toISOString().split("T")[0];
      } catch (error) {
        console.warn("Invalid date format:", itemDate);
      }
    }

    const matchDate = !selectedDate || formattedDate === selectedDate;

    return matchCustomer && matchDate;
  };

  const filteredOrders = orders.filter((order) => applyFilters(order, "customer_id", "DeliveryDate"));
  const filteredCustomers = customers.filter((customer) => applyFilters(customer, "CustomerId", "DeliveryDate"));
  const filteredEnquiries = enquiries.filter((enquiry) => applyFilters(enquiry, "CustomerId", "DeliveryDate"));
  const filteredIssues = issues.filter((issue) => applyFilters(issue, "CustomerId", "DeliveryDate"));

  const orderColumns = [
    { title: "Customer Name", dataIndex: "CustomerName", key: "CustomerName" },
    { title: "Order Number", dataIndex: "OrderNumber", key: "OrderNumber" },
    { title: "Item", dataIndex: "Item", key: "Item" },
    {
      title: "Quantity",
      key: "Quantity",
      render: (_, record) => {
        return `${record.Quantity}${record.Unit ? " (" + record.Unit + ")" : ""}`;
      },
    },
    { title: "Notes", dataIndex: "Notes", key: "Notes" },
    // { title: "Status", dataIndex: "Status", key: "Status", render: (text) => <Tag color="green">{text}</Tag> },
    {
      title: "Status",
      dataIndex: "Status",
      key: "Status",
      filters: [
        { text: "Pending", value: "pending" },
        { text: "Completed", value: "completed" },
      ],
      onFilter: (value, record) => record.Status.toLowerCase() === value,
      render: (text) => (
        <Tag color={text.toLowerCase() === "completed" ? "green" : "orange"}>
          {text}
        </Tag>
      ),
    },
    { title: "Amount ($)", dataIndex: "Amount", key: "Amount" },
    { title: "Delivery Address", dataIndex: "DeliveryAddress", key: "DeliveryAddress", render: (text) => text || "-" },
    { title: "Delivery Time", dataIndex: "DeliveryTime", key: "DeliveryTime", render: (text) => text || "-" },
    {
      title: "Delivery Method",
      dataIndex: "DeliveryMethod",
      key: "DeliveryMethod",
      render: (method) => (method ? <Tag color="blue">{method}</Tag> : "-"),
    },
    // { title: "Action", key: "action", render: () => <Button size="small" type="primary">Done</Button> },
  ];

  orderColumns.push({
    title: "Action",
    key: "action",
    render: (_, record) => renderActionMenu(record),
  });
  

  const customerColumns = [
    { title: "Customer ID", dataIndex: "CustomerId", key: "CustomerId" },
    { title: "Customer Name", dataIndex: "CustomerName", key: "CustomerName" },
    { title: "Email", dataIndex: "Email", key: "Email" },
    { title: "Created Date", dataIndex: "DeliveryDate", key: "DeliveryDate" },
    // { title: "Updated Date", dataIndex: "UpdatedDate", key: "UpdatedDate" },
  ];

  const issueColumns = [
    { title: "Issue ID", dataIndex: "IssueId", key: "IssueId" },
    { title: "Customer ID", dataIndex: "CustomerId", key: "CustomerId" },
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
      },
    },
    { title: "Status", dataIndex: "Status", key: "Status" },
    {
      title: "Created Date",
      dataIndex: "DeliveryDate",
      key: "DeliveryDate",
      render: (date) => (date ? new Date(date).toLocaleDateString() : ""),
    },
    {
      title: "Updated Date",
      dataIndex: "UpdatedDate",
      key: "UpdatedDate",
      render: (date) => (date ? new Date(date).toLocaleDateString() : ""),
    },
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
      },
    },
    { title: "Status", dataIndex: "Status", key: "Status" },
    {
      title: "Follow Up Date",
      dataIndex: "FollowUpDate",
      key: "FollowUpDate",
      render: (date) => (date ? new Date(date).toLocaleDateString() : ""),
    },
    {
      title: "Enquiry Created Date",
      dataIndex: "DeliveryDate",
      key: "DeliveryDate",
      render: (date) => (date ? new Date(date).toLocaleDateString() : ""),
    },
    // {
    //   title: "Updated Date",
    //   dataIndex: "UpdatedDate",
    //   key: "UpdatedDate",
    //   render: (date) => (date ? new Date(date).toLocaleDateString() : ""),
    // },
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

    orders.forEach((order) => {
      const id = order.customer_id || order.CustomerId;
      if (id) customerIds.push(id);
    });

    customers.forEach((customer) => {
      const id = customer.CustomerId || customer.customer_id;
      if (id) customerIds.push(id);
    });

    enquiries.forEach((enquiry) => {
      const id = enquiry.CustomerId || enquiry.customer_id;
      if (id) customerIds.push(id);
    });

    issues.forEach((issue) => {
      const id = issue.CustomerId || issue.customer_id;
      if (id) customerIds.push(id);
    });

    return [...new Set(customerIds)].filter((id) => id);
  };

  const calculateMetrics = () => {
    const totalOrders = orders.length;
    const totalCustomers = customers.length;
    const totalEnquiries = enquiries.length;
    const totalIssues = issues.length;

    // Calculate total revenue with explicit parsing and NaN handling
    const totalRevenue = orders.reduce((sum, order) => {
      const amount = parseFloat(order.Amount);
      return sum + (isNaN(amount) ? 0 : amount);
    }, 0);
    
    // Calculate average order value with proper formatting
    const rawAvgOrderValue = totalOrders > 0 ? totalRevenue / totalOrders : 0;
    const averageOrderValue = isNaN(rawAvgOrderValue) ? "0.00" : rawAvgOrderValue.toFixed(2);

    const today = new Date().toISOString().split("T")[0];
    const todayOrders = orders.filter((order) => {
      const orderDate = order.DeliveryDate?.split("T")[0];
      return orderDate === today;
    }).length;

    const ordersByStatus = {};
    filteredOrders.forEach((order) => {
      const status = order.Status || "Pending";
      ordersByStatus[status] = (ordersByStatus[status] || 0) + 1;
    });

    const customerOrderCounts = {};
    filteredOrders.forEach((order) => {
      const customerId = order.customer_id;
      if (customerId) {
        customerOrderCounts[customerId] = (customerOrderCounts[customerId] || 0) + 1;
      }
    });

    const returningCustomers = Object.values(customerOrderCounts).filter((count) => count > 1).length;
    const retentionRate = totalCustomers > 0 ? Math.round((returningCustomers / totalCustomers) * 100) : 0;

    const completedOrders = filteredOrders.filter((order) => order.Status === "completed").length;
    const completionRate = totalOrders > 0 ? `${Math.round((completedOrders / totalOrders) * 100)}%` : "0%";

    // Calculate total order value for filtered orders with explicit parsing
    const totalOrderValue = filteredOrders.reduce((sum, order) => {
      const amount = parseFloat(order.Amount);
      return sum + (isNaN(amount) ? 0 : amount);
    }, 0);
    
    // Format the display value with dollar sign
    const formattedAvgOrderValue = totalOrders > 0 ? `$${(totalOrderValue / totalOrders).toFixed(2)}` : "$0.00";

    const resolvedIssues = filteredIssues.filter((issue) => issue.Status === "resolved").length;
    const resolutionRate = totalIssues > 0 ? `${Math.round((resolvedIssues / totalIssues) * 100)}%` : "0%";

    // Calculate total messages that should have responses
    const totalMessages = totalOrders + totalEnquiries + totalIssues;
    
    // Calculate response metrics
    const totalResponses = responseMetrics.length;
    const responseRate = totalMessages > 0 ? Math.round((totalResponses / totalMessages) * 100) : 0;
    
    // Calculate average response time
    const totalResponseTime = responseMetrics.reduce((sum, metric) => sum + (metric.ResponseTimeSeconds || 0), 0);
    const avgResponseTimeSeconds = totalResponses > 0 ? totalResponseTime / totalResponses : 0;

    let avgResponseTime;
    if (avgResponseTimeSeconds < 1) {
      avgResponseTime = `${Math.round(avgResponseTimeSeconds * 1000)} ms`;
    } else if (avgResponseTimeSeconds < 60) {
      avgResponseTime = `${avgResponseTimeSeconds.toFixed(2)} sec`;
    } else {
      avgResponseTime = `${(avgResponseTimeSeconds / 60).toFixed(2)} min`;
    }

    const responseTypes = {};
    responseMetrics.forEach((metric) => {
      const type = metric.ResponseType || "unknown";
      responseTypes[type] = (responseTypes[type] || 0) + 1;
    });

    return {
      totalOrders,
      totalCustomers,
      totalEnquiries,
      totalIssues,
      totalRevenue,
      averageOrderValue,
      todayOrders,
      pendingOrders: ordersByStatus["Pending"] || 0,
      retentionRate: `${retentionRate}%`,
      responseRate: `${responseRate}%`, // Calculated based on total messages and responses
      completedOrders,
      completionRate,
      avgOrderValue: formattedAvgOrderValue, // Use the formatted value with dollar sign
      resolvedIssues,
      resolutionRate,
      avgResponseTime,
      avgResponseTimeSeconds,
      totalResponses,
      responseTypes,
    };
  };

  const stats = calculateMetrics();

  const isTabDataLoading = () => {
    switch (tab) {
      case "orders":
        return dataLoadingState.orders;
      case "customers":
        return dataLoadingState.customers;
      case "enquiries":
        return dataLoadingState.enquiries;
      case "issues":
        return dataLoadingState.issues;
      default:
        return false;
    }
  };

  const currentData = getCurrentData();
  const hasData = currentData && currentData.length > 0;

  const handleExport = (fileType) => {
    //const data = getCurrentData();
    const data = visibleData.length ? visibleData : getCurrentData();
    const worksheet = XLSX.utils.json_to_sheet(data);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Data");

    const excelBuffer = XLSX.write(workbook, { bookType: fileType === "excel" ? "xlsx" : "csv", type: "array" });
    const blob = new Blob([excelBuffer], { type: "application/octet-stream" });
    saveAs(blob, `dashboard_data_${tab}.${fileType === "excel" ? "xlsx" : "csv"}`);
  };

  const handleMarkAsCompleted = async (orderNumber) => {
    try {
      await updateOrderStatus(orderNumber, "completed");
      setOrders((prev) =>
        prev.map((order) =>
          order.OrderNumber === orderNumber ? { ...order, Status: "completed" } : order
        )
      );
    } catch (error) {
      console.error("Failed to update order status:", error);
    }
  };
  
  
  const handleRemove = (orderNumber) => {
    setOrders((prev) => prev.filter((order) => order.OrderNumber !== orderNumber));
  };
  
  
  const renderActionMenu = (record) => {
    const items = [
      {
        key: "mark-completed",
        label: "Mark as Completed",
        onClick: () => handleMarkAsCompleted(record.OrderNumber),
      },
      {
        key: "reply",
        label: "Reply (Coming Soon)",
        disabled: true,
      },
    ];
  
    // if (record.Status === "completed") {
    //   return (
    //     <Button size="small" danger onClick={() => handleRemove(record.order_id)}>
    //       Remove
    //     </Button>
    //   );
    // }
  
    if (record.Status === "completed") {
      return (
        <div className="flex gap-2">
          {/* <button
            onClick={() => handleRemove(record.OrderNumber)}
            className="px-4 py-1 text-xs sm:text-sm rounded-full font-semibold shadow-md text-white bg-gradient-to-r from-pink-400 to-orange-400 hover:from-orange-400 hover:to-pink-400 transition duration-300"
          >
            Remove
          </button> */}
          <button
            onClick={() => handleUndo(record.OrderNumber)}
            className="px-4 py-1 text-xs sm:text-sm rounded-full font-semibold shadow-md text-white bg-gradient-to-r from-pink-400 to-orange-400 hover:from-orange-400 hover:to-pink-400 transition duration-300"
          >
            Undo
          </button>
        </div>
      );
    }
    
    


    return (
      <Dropdown menu={{ items }}>
        <MoreOutlined style={{ fontSize: 20, cursor: "pointer" }} />
      </Dropdown>
    );
  };
  
  const handleUndo = async (orderNumber) => {
    try {
      await updateOrderStatus(orderNumber, "pending");
      setOrders((prev) =>
        prev.map((order) =>
          order.OrderNumber === orderNumber ? { ...order, Status: "pending" } : order
        )
      );
    } catch (error) {
      console.error("Failed to undo order status:", error);
    }
  };
  

  return (
    <>
      <DashboardHeader user={clerkUser} onLogout={handleLogout} onUpdateProfile={handleUpdateProfile} />
      <div className="min-h-screen bg-gray-50 space-y-6 pt-24 px-4 sm:px-6">
        {/* Setup Banner for new users */}
        <SetupBanner 
          visible={showSetupBanner} 
          onClose={() => setShowSetupBanner(false)} 
        />
        
        {/* Error Banner for configuration issues */}
        {clerkUser && <ErrorBanner userId={clerkUser.id} />}
        {/* Stats Overview */}
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Business Overview</h2>
          {dataLoadingState.metrics ? (
            <CardLoader count={4} />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-blue-500">
                <h3 className="text-sm font-medium text-gray-500">Total Orders</h3>
                <p className="text-2xl font-bold">{stats.totalOrders}</p>
                <div className="mt-2 flex justify-between text-sm">
                  <span className="text-green-600">{stats.todayOrders} today</span>
                  <span className="text-gray-500">{stats.pendingOrders} pending</span>
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-green-500">
                <h3 className="text-sm font-medium text-gray-500">Total Revenue</h3>
                <p className="text-2xl font-bold">${stats.totalRevenue.toFixed(2)}</p>
                <div className="mt-2 text-sm text-gray-500">Avg. Order: ${stats.averageOrderValue}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-purple-500">
                <h3 className="text-sm font-medium text-gray-500">Total Customers</h3>
                <p className="text-2xl font-bold">{stats.totalCustomers}</p>
                <div className="mt-2 text-sm text-gray-500">Retention Rate: {stats.retentionRate}</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-md border-l-4 border-yellow-500">
                <h3 className="text-sm font-medium text-gray-500">Response Rate</h3>
                <p className="text-2xl font-bold">{stats.responseRate}</p>
                <div className="mt-2 text-sm text-gray-500">Avg. Time: {stats.avgResponseTime}</div>
              </div>
            </div>
          )}
        </div>

        {/* Additional Metrics */}
        {dataLoadingState.metrics ? (
          <div className="mb-6">
            <CardLoader count={3} />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Sales Metrics */}
            <div className="bg-white p-4 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-3">Sales Overview</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="border-r pr-4">
                  <h4 className="text-sm font-medium text-gray-500">Total Orders</h4>
                  <p className="text-xl font-bold">{stats.totalOrders}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Total Customers</h4>
                  <p className="text-xl font-bold">{stats.totalCustomers}</p>
                </div>
                <div className="border-r pr-4">
                  <h4 className="text-sm font-medium text-gray-500">Avg Order Value</h4>
                  <p className="text-xl font-bold text-green-600">{stats.avgOrderValue}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Completion Rate</h4>
                  <p className="text-xl font-bold">{stats.completionRate}</p>
                </div>
              </div>
              <div className="mt-4">
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">Order Completion</span>
                  <span className="text-sm font-medium text-gray-700">{stats.completedOrders} orders</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full"
                    style={{
                      width: `${stats.totalOrders ? (stats.completedOrders / stats.totalOrders) * 100 : 0}%`,
                    }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Support Metrics */}
            <div className="bg-white p-4 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-3">Support Performance</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="border-r pr-4">
                  <h4 className="text-sm font-medium text-gray-500">Total Enquiries</h4>
                  <p className="text-xl font-bold">{stats.totalEnquiries}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Total Issues</h4>
                  <p className="text-xl font-bold">{stats.totalIssues}</p>
                </div>
                <div className="border-r pr-4">
                  <h4 className="text-sm font-medium text-gray-500">Resolution Rate</h4>
                  <p className="text-xl font-bold text-green-600">{stats.resolutionRate}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Avg. Response</h4>
                  <p className="text-xl font-bold">{stats.avgResponseTime}</p>
                </div>
              </div>
            </div>

            {/* Waffy Response Metrics */}
            <div className="bg-white p-4 rounded-lg shadow-md">
              <h3 className="text-lg font-semibold mb-3">Waffy Response Metrics</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="border-r pr-4">
                  <h4 className="text-sm font-medium text-gray-500">Total Responses</h4>
                  <p className="text-xl font-bold">{stats.totalResponses}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Avg. Response Time</h4>
                  <p className="text-xl font-bold text-green-600">{stats.avgResponseTime}</p>
                </div>
              </div>
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Response Speed</h4>
                <Progress
                  percent={Math.min(100, Math.max(0, 100 - stats.avgResponseTimeSeconds * 10))}
                  status="active"
                  strokeColor={{
                    "0%": "#108ee9",
                    "100%": "#87d068",
                  }}
                  format={() => stats.avgResponseTime}
                />
              </div>
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Response Types</h4>
                <div className="space-y-2">
                  {Object.entries(stats.responseTypes || {}).map(([type, count]) => (
                    <div key={type} className="flex justify-between items-center">
                      <span className="text-sm capitalize">{type.replace("_", " ")}</span>
                      <Tag
                        color={
                          type === "order_confirmation"
                            ? "green"
                            : type === "issue_acknowledgement"
                            ? "orange"
                            : type === "enquiry_response"
                            ? "blue"
                            : "default"
                        }
                      >
                        {count}
                      </Tag>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

         {/* Tabs */}
         <div className="flex gap-4 mb-6">
          {["orders", "customers", "enquiries", "issues"].map((tabName) => (
            <button
              key={tabName}
              onClick={() => setTab(tabName)}
              className={`px-6 py-2 rounded-full font-semibold shadow-md text-white bg-gradient-to-r from-pink-400 to-orange-400 hover:from-orange-400 hover:to-pink-400 transition duration-300 ${
                tab === tabName ? "border-4 border-yellow-300 scale-105" : "border-none"
              }`}
            >
              {tabName.charAt(0).toUpperCase() + tabName.slice(1)}
            </button>
          ))}
        </div>

        {/* Filter & Export Row */}
        <div className="flex flex-wrap gap-4 mb-6 items-end justify-between">
          <div className="flex flex-wrap gap-4 items-end">
            <div className="flex flex-col">
              <label className="text-sm font-semibold mb-1">Customer ID:</label>
              <select
                className="p-2 border rounded w-48"
                value={customerFilter}
                onChange={(e) => setCustomerFilter(e.target.value)}
              >
                <option value="">All Customers</option>
                {[...new Set([...orders, ...customers, ...enquiries, ...issues].map(item => item.CustomerId || item.customer_id).filter(Boolean))].map((id) => (
                  <option key={id} value={id}>{id}</option>
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
          <div className="flex gap-2">
            <Button onClick={() => handleExport("excel")}
              disabled={!hasData}
              className={`px-6 py-2 rounded-full font-semibold shadow-md text-white ${hasData ? 'bg-gradient-to-r from-pink-400 to-orange-400 hover:from-orange-400 hover:to-pink-400' : 'bg-gray-300 cursor-not-allowed'}`}>
              Export to Excel
            </Button>
            <Button onClick={() => handleExport("csv")}
              disabled={!hasData}
              className={`px-6 py-2 rounded-full font-semibold shadow-md text-white ${hasData ? 'bg-gradient-to-r from-pink-400 to-orange-400 hover:from-orange-400 hover:to-pink-400' : 'bg-gray-300 cursor-not-allowed'}`}>
              Export to CSV
            </Button>
          </div>
        </div>

        {/* Table Rendering */}
        {isTabDataLoading() ? (
          <div className="py-4">
            <div className="mb-4 flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-700">{tab.charAt(0).toUpperCase() + tab.slice(1)}</h3>
              <div className="flex items-center">
                <Loader size="sm" />
                <span className="ml-2 text-sm text-gray-500">Loading {tab}...</span>
              </div>
            </div>
            <TableLoader rows={5} columns={getCurrentColumns().length || 5} className="shadow-sm" />
          </div>
        ) : (
          <div className="overflow-x-auto -mx-4 sm:mx-0">
            <Table
              columns={getCurrentColumns()}
              dataSource={getCurrentData().map((item, index) => ({ ...item, key: index }))}
              pagination={{ pageSize: 10 }}
              onChange={(pagination, filters, sorter, extra) => {
                setVisibleData(extra.currentDataSource);
              }}
              scroll={{ x: 'max-content' }}
              size="small"
              className="whitespace-nowrap"
              locale={{
                emptyText: (
                  <div className="py-8 text-center">
                    <p className="text-gray-500">No data available</p>
                  </div>
                ),
              }}
            />
          </div>
        )}
      </div>
    </>
  );
};

export default Dashboard;