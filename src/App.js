import React from "react";
import { SignedIn, SignedOut, SignIn, UserButton } from "@clerk/clerk-react";
import { messages } from "./data/messages";
import { MessageTab } from "./components/MessageTab";

function App() {
  const handleReply = (id) => {
    alert(`Reply to message ID: ${id}`);
  };

  const sortedMessages = ["Emergency", "Important", "Routine"].flatMap(priority =>
    messages.filter(msg => msg.priority === priority)
  );

  return (
    <div className="min-h-screen bg-gray-100">
      {/* 🌈 Vibrant Top Nav */}
      <header className="sticky top-0 z-10 bg-gradient-to-r from-pink-500 to-yellow-400 shadow-md px-6 py-4 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white tracking-wide">WAffy</h1>
        <UserButton afterSignOutUrl="/" />
      </header>

      {/* 📦 Main Content */}
      <main className="p-6 space-y-4">
        <SignedIn>
          {sortedMessages.map((msg) => (
            <MessageTab key={msg.id} message={msg} onReply={handleReply} />
          ))}
        </SignedIn>

        <SignedOut>
          <div className="flex flex-col items-center justify-center min-h-[80vh]">
            <h1 className="text-2xl font-bold mb-4 text-blue-600">Welcome to WAffy</h1>
            <SignIn routing="hash" />
          </div>
        </SignedOut>
      </main>
    </div>
  );
}

export default App;
