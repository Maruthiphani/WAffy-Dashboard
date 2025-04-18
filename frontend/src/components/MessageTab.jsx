import React from "react";

const priorityColors = {
  Emergency: "border-red-500 bg-red-100",
  Important: "border-orange-500 bg-orange-100",
  Routine: "border-green-500 bg-green-100",
};

export const MessageTab = ({ message, onReply }) => {
  return (
    <div
      className={`w-full border-l-4 p-6 rounded shadow-md ${priorityColors[message.priority]}`}
    >
      <div className="flex justify-between items-start flex-wrap gap-4">
        <div className="flex-1 min-w-0">
          <p className="text-base text-gray-800 font-medium break-words">
            {message.message}
          </p>
          <p className="text-xs text-gray-500 mt-2">
            {new Date(message.timestamp).toLocaleString()}
          </p>
        </div>
        <button
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition"
          onClick={() => onReply(message.id)}
        >
          Reply
        </button>
      </div>
    </div>
  );
};
