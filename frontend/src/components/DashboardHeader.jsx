import React from "react";

const DashboardHeader = ({ user, onLogout, onUpdateProfile }) => (
  <div className="flex items-center justify-between py-4 px-6 bg-white shadow rounded-lg mb-4">
    <h1 className="text-2xl font-bold">Dashboard</h1>
    <div className="flex items-center space-x-4">
      <img
        src={user?.profileImage || `https://ui-avatars.com/api/?name=${user?.firstName || "U"}+${user?.lastName || "S"}&background=FFB6C1&color=fff`}
        alt="Profile"
        className="w-9 h-9 rounded-full border"
      />
      <span className="font-medium text-gray-700">{user?.firstName} {user?.lastName}</span>
      <button
        onClick={onUpdateProfile}
        className="px-3 py-1 text-sm bg-yellow-400 hover:bg-yellow-500 text-white rounded shadow"
      >
        Update Profile
      </button>
      <button
        onClick={onLogout}
        className="px-3 py-1 text-sm bg-gradient-to-r from-pink-400 to-yellow-400 hover:from-pink-500 hover:to-yellow-500 text-white rounded shadow"
      >
        Logout
      </button>
    </div>
  </div>
);

export default DashboardHeader;
