import React from "react";
import { useUser, useClerk } from "@clerk/clerk-react";

const DashboardHeader = () => {
  const { user } = useUser();
  const { signOut, openUserProfile } = useClerk();

  if (!user) return null;

  const displayName = user.firstName || user.lastName
    ? `${user.firstName || ""} ${user.lastName || ""}`.trim()
    : user.primaryEmailAddress?.emailAddress;

  return (
    <div className="fixed top-0 left-0 w-full z-30 bg-gradient-to-r from-pink-400 to-yellow-400 shadow-md">
      <div className="flex items-center justify-end py-3 px-6 max-w-screen-2xl mx-auto">
        <div className="flex items-center space-x-4">
          <img
            src={user.imageUrl || `https://ui-avatars.com/api/?name=${user.firstName || "U"}+${user.lastName || "S"}&background=FFB6C1&color=fff`}
            alt="Profile"
            className="w-9 h-9 rounded-full border-2 border-white shadow"
          />
          <span className="font-medium text-white hidden sm:inline">{displayName}</span>
          <button
            onClick={() => openUserProfile({ path: "/security" })}
            className="px-3 py-1 text-sm bg-white text-pink-600 hover:bg-gray-100 rounded shadow transition"
          >
            Update Password
          </button>
          <button
            onClick={() => signOut()}
            className="px-3 py-1 text-sm bg-white text-pink-600 hover:bg-gray-100 rounded shadow transition"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardHeader;
