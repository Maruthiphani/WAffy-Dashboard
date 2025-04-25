import React from "react";

const UserProfile = ({ user, onLogout }) => {
  return (
    <div className="flex items-center space-x-4 p-4 bg-white rounded-lg shadow">
      <img
        src={user?.profileImage || `https://ui-avatars.com/api/?name=${user?.firstName || "U"}+${user?.lastName || "S"}&background=FFB6C1&color=fff`}
        alt="Profile"
        className="w-12 h-12 rounded-full border"
      />
      <div>
        <div className="font-semibold text-gray-900">{user?.firstName} {user?.lastName}</div>
        <div className="text-sm text-gray-500">{user?.email}</div>
      </div>
      <button
        onClick={onLogout}
        className="ml-auto px-4 py-2 bg-gradient-to-r from-pink-400 to-yellow-400 text-white rounded shadow hover:from-pink-500 hover:to-yellow-500"
      >
        Logout
      </button>
    </div>
  );
};

export default UserProfile;
