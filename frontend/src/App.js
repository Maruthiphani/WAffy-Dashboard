import React, { useState } from "react";
import { SignedIn, SignedOut, SignIn, SignUp, UserButton } from "@clerk/clerk-react";
import { messages } from "./data/messages";
import { MessageTab } from "./components/MessageTab";

function App() {
  const [activeTab, setActiveTab] = useState("signup");
  const [activeFaq, setActiveFaq] = useState(null);
  
  const handleReply = (id) => {
    alert(`Reply to message ID: ${id}`);
  };

  const sortedMessages = ["Emergency", "Important", "Routine"].flatMap(priority =>
    messages.filter(msg => msg.priority === priority)
  );

  const toggleFaq = (index) => {
    setActiveFaq(activeFaq === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Vibrant Top Nav */}
      <header className="sticky top-0 z-10 bg-gradient-to-r from-pink-500 to-yellow-400 shadow-md px-6 py-4 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white tracking-wide">WAffy</h1>
        <UserButton afterSignOutUrl="/" />
      </header>

      {/* Main Content */}
      <main className="p-6">
        <SignedIn>
          <div className="space-y-4">
            {sortedMessages.map((msg) => (
              <MessageTab key={msg.id} message={msg} onReply={handleReply} />
            ))}
          </div>
        </SignedIn>

        <SignedOut>
          <div className="w-full mx-auto">
            {/* Hero Component with Signup/Login - Full Width */}
            <div className="bg-white rounded-xl shadow-xl overflow-hidden">
              <div className="flex flex-col lg:flex-row">
                {/* Left side - Hero content */}
                <div className="lg:w-3/5 p-8 lg:p-12 flex flex-col justify-center">
                  <h1 className="text-4xl lg:text-5xl font-bold text-gray-800 mb-6">
                    Organize WhatsApp Messages, Never Miss a Sale
                  </h1>
                  <p className="text-xl text-gray-600 mb-8">
                    WAffy tags your customer chats and keeps your CRM in sync, helping small businesses respond faster.
                  </p>
                  <div className="flex flex-wrap gap-4">
                    <button 
                      onClick={() => setActiveTab("signup")}
                      className="bg-gradient-to-r from-pink-500 to-yellow-400 text-white font-bold py-3 px-8 rounded-lg shadow-lg hover:shadow-xl transition duration-300"
                    >
                      Get Started
                    </button>
                    <button 
                      onClick={() => setActiveTab("login")}
                      className="bg-white text-gray-700 border border-gray-300 font-bold py-3 px-8 rounded-lg shadow hover:shadow-md transition duration-300"
                    >
                      Login
                    </button>
                  </div>
                  
                  {/* Supported platforms badges */}
                  <div className="mt-12">
                    <p className="text-sm text-gray-500 mb-4">Integrates with:</p>
                    <div className="flex flex-wrap items-center gap-4">
                      <span className="bg-gray-100 px-4 py-2 rounded-full text-sm font-medium">WhatsApp Cloud API</span>
                      <span className="bg-gray-100 px-4 py-2 rounded-full text-sm font-medium">HubSpot</span>
                      <span className="bg-gray-100 px-4 py-2 rounded-full text-sm font-medium">Excel</span>
                    </div>
                  </div>
                </div>
                
                {/* Right side - Auth forms with fixed height */}
                <div className="lg:w-2/5 bg-gray-50 p-8 flex flex-col">
                  <div className="flex mb-6 justify-center">
                    <button 
                      className={`flex-1 py-2 text-center border-b-2 ${activeTab === "login" ? "border-pink-500 text-pink-500" : "border-transparent hover:text-pink-500"} focus:outline-none`}
                      onClick={() => setActiveTab("login")}
                    >
                      Login
                    </button>
                    <button 
                      className={`flex-1 py-2 text-center border-b-2 ${activeTab === "signup" ? "border-pink-500 text-pink-500" : "border-transparent hover:text-pink-500"} focus:outline-none`}
                      onClick={() => setActiveTab("signup")}
                    >
                      Sign Up
                    </button>
                  </div>
                  <div className="min-h-[600px] overflow-y-auto">
                    <div className="w-full flex justify-center">
                      {activeTab === "login" ? (
                        <SignIn routing="hash" />
                      ) : (
                        <SignUp routing="hash" />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Feature Highlights */}
            <div className="mt-16">
              <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">Key Features</h2>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                <div className="bg-white p-6 rounded-lg shadow-md text-center">
                  <div className="w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">🔍</span>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Smart Classification</h3>
                  <p className="text-gray-600">Automatically categorize messages by priority and intent.</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-md text-center">
                  <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">⚡</span>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Instant Notifications</h3>
                  <p className="text-gray-600">Get alerted about high-priority messages immediately.</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-md text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">🔄</span>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">CRM Integration</h3>
                  <p className="text-gray-600">Sync customer data automatically with your existing systems.</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-md text-center">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl">📊</span>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Analytics Dashboard</h3>
                  <p className="text-gray-600">Track response times and customer engagement metrics.</p>
                </div>
              </div>
            </div>

            {/* Benefits Section */}
            <div className="mt-16">
              <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">Benefits for Small Brands</h2>
              <div className="grid md:grid-cols-3 gap-8">
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h3 className="text-xl font-semibold mb-2">Speed</h3>
                  <p className="text-gray-600">Respond to customer inquiries faster with prioritized messages.</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h3 className="text-xl font-semibold mb-2">Organization</h3>
                  <p className="text-gray-600">Keep all customer conversations neatly organized and accessible.</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <h3 className="text-xl font-semibold mb-2">Data</h3>
                  <p className="text-gray-600">Gain valuable insights from customer interactions to improve your business.</p>
                </div>
              </div>
            </div>

            {/* Testimonials Section */}
            <div className="mt-16 bg-gray-50 py-12 px-6 rounded-xl">
              <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">What Our Customers Say</h2>
              <div className="grid md:grid-cols-3 gap-8">
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-pink-200 rounded-full mr-4 flex items-center justify-center text-pink-500 font-bold">SJ</div>
                    <div>
                      <h4 className="font-semibold">Sarah Johnson</h4>
                      <p className="text-sm text-gray-500">Small Business Owner</p>
                    </div>
                  </div>
                  <p className="text-gray-600">"WAffy has transformed how we handle customer inquiries. We're responding faster and never miss important messages."</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-yellow-200 rounded-full mr-4 flex items-center justify-center text-yellow-500 font-bold">MT</div>
                    <div>
                      <h4 className="font-semibold">Michael Torres</h4>
                      <p className="text-sm text-gray-500">E-commerce Manager</p>
                    </div>
                  </div>
                  <p className="text-gray-600">"The automatic tagging feature saves us hours every week. Our team can focus on selling instead of sorting messages."</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow-md">
                  <div className="flex items-center mb-4">
                    <div className="w-12 h-12 bg-blue-200 rounded-full mr-4 flex items-center justify-center text-blue-500 font-bold">LP</div>
                    <div>
                      <h4 className="font-semibold">Lisa Patel</h4>
                      <p className="text-sm text-gray-500">Marketing Director</p>
                    </div>
                  </div>
                  <p className="text-gray-600">"The HubSpot integration is seamless. All our customer data is in one place, making our marketing campaigns much more effective."</p>
                </div>
              </div>
            </div>

            {/* FAQ Section */}
            <div className="mt-16">
              <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">Frequently Asked Questions</h2>
              <div className="max-w-3xl mx-auto space-y-4">
                {[
                  {
                    question: "How does WAffy integrate with WhatsApp?",
                    answer: "WAffy connects directly to your WhatsApp Business API account, requiring minimal setup and no technical knowledge. Once connected, it automatically processes all incoming messages."
                  },
                  {
                    question: "Is my customer data secure?",
                    answer: "Absolutely. WAffy employs end-to-end encryption and complies with GDPR and other data protection regulations. Your customer data is never shared with third parties without your explicit permission."
                  },
                  {
                    question: "Can I customize how messages are categorized?",
                    answer: "Yes, WAffy allows you to create custom tags and priority levels based on your business needs. You can also set up automated rules for message classification."
                  },
                  {
                    question: "How long does it take to set up?",
                    answer: "Most businesses are up and running within 15 minutes. Our guided setup process walks you through connecting your WhatsApp Business account and configuring your preferences."
                  }
                ].map((faq, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden">
                    <button
                      className="w-full p-6 text-left flex justify-between items-center focus:outline-none"
                      onClick={() => toggleFaq(index)}
                    >
                      <h3 className="text-lg font-semibold">{faq.question}</h3>
                      <span className={`transform transition-transform duration-200 ${activeFaq === index ? 'rotate-180' : ''}`}>
                        ▼
                      </span>
                    </button>
                    <div className={`px-6 pb-6 ${activeFaq === index ? 'block' : 'hidden'}`}>
                      <p className="text-gray-600">{faq.answer}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* CTA Banner */}
            <div className="mt-16 bg-gradient-to-r from-pink-500 to-yellow-400 py-12 px-6 rounded-xl text-center">
              <h2 className="text-3xl font-bold text-white mb-4">Ready to transform your customer communication?</h2>
              <p className="text-white text-xl mb-8 max-w-2xl mx-auto">Join hundreds of small businesses already using WAffy to improve response times and never miss a sale.</p>
              <button 
                onClick={() => {
                  setActiveTab("signup");
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
                className="bg-white text-pink-500 font-bold py-3 px-8 rounded-lg shadow-lg hover:shadow-xl transition duration-300"
              >
                Start Your Free Trial
              </button>
            </div>

            {/* Footer */}
            <footer className="mt-16 pt-12 pb-6 border-t border-gray-200">
              <div className="grid md:grid-cols-4 gap-8 mb-8">
                <div>
                  <h3 className="font-bold text-lg mb-4">WAffy</h3>
                  <p className="text-gray-600">Helping small businesses organize WhatsApp messages and improve customer communication.</p>
                </div>
                <div>
                  <h4 className="font-bold mb-4">Product</h4>
                  <ul className="space-y-2">
                    <li><a href="#" className="text-gray-600 hover:text-pink-500">Features</a></li>
                    <li><a href="#" className="text-gray-600 hover:text-pink-500">Pricing</a></li>
                    <li><a href="#" className="text-gray-600 hover:text-pink-500">Integrations</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold mb-4">Resources</h4>
                  <ul className="space-y-2">
                    <li><a href="#" className="text-gray-600 hover:text-pink-500">Documentation</a></li>
                    <li><a href="#" className="text-gray-600 hover:text-pink-500">Blog</a></li>
                    <li><a href="#" className="text-gray-600 hover:text-pink-500">Support</a></li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold mb-4">Company</h4>
                  <ul className="space-y-2">
                    <li><a href="#" className="text-gray-600 hover:text-pink-500">About</a></li>
                    <li><a href="#" className="text-gray-600 hover:text-pink-500">Contact</a></li>
                    <li><a href="#" className="text-gray-600 hover:text-pink-500">Privacy Policy</a></li>
                  </ul>
                </div>
              </div>
              <div className="text-center text-gray-500 text-sm">
                {new Date().getFullYear()} WAffy. All rights reserved.
              </div>
            </footer>
          </div>
        </SignedOut>
      </main>
    </div>
  );
}

export default App;
