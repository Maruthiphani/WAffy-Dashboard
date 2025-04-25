import React, { useState } from "react";
import { messages } from "../data/messages";
import { MessageTab } from "../components/MessageTab";
import DashboardHeader from "../components/DashboardHeader";

const Dashboard = () => {
  // Simulated user data (replace with Clerk or API integration as needed)
  const [user] = useState({
    firstName: "Jane",
    lastName: "Doe",
    email: "jane.doe@example.com",
    profileImage: ""
  });

  const handleLogout = () => {
    // Clerk logout logic or redirect
    alert("Logged out!");
    // window.location.href = '/';
  };

  const handleUpdateProfile = () => {
    // Clerk profile update logic or open a modal
    alert("Update profile clicked!");
  };

  const handleReply = (id) => {
    alert(`Reply to message ID: ${id}`);
  };

  const sortedMessages = ["Emergency", "Important", "Routine"].flatMap(priority =>
    messages.filter(msg => msg.priority === priority)
  );

  // Calculate statistics
  const stats = {
    total: messages.length,
    emergency: messages.filter(msg => msg.priority === "Emergency").length,
    important: messages.filter(msg => msg.priority === "Important").length,
    routine: messages.filter(msg => msg.priority === "Routine").length,
    responseRate: "87%", // Placeholder
    avgResponseTime: "28 min" // Placeholder
  };

  // Priority breakdown percentages
  const emergencyPercent = Math.round((stats.emergency / stats.total) * 100);
  const importantPercent = Math.round((stats.important / stats.total) * 100);
  const routinePercent = Math.round((stats.routine / stats.total) * 100);

  return (
    <div className="space-y-6">
      <DashboardHeader user={user} onLogout={handleLogout} onUpdateProfile={handleUpdateProfile} />
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-md">
          <h3 className="text-sm font-medium text-gray-500">Total Messages</h3>
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
      
      {/* Priority Breakdown */}
      <div className="bg-white p-6 rounded-lg shadow-md">
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
      </div>
      
      {/* Messages */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Recent Messages</h2>
        {sortedMessages.map((msg) => (
          <MessageTab key={msg.id} message={msg} onReply={handleReply} />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
