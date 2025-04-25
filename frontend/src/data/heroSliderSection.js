import React, { useState, useEffect } from 'react';
import { SignedOut, SignIn, SignUp } from '@clerk/clerk-react';

export default function HeroSliderSection({ activeTab, setActiveTab }) {
  const messages = [
    {
      title: 'Save Time with WAffy',
      text: 'Streamline your messaging process and boost productivity.'
    },
    {
      title: 'Smart Chat Tagging',
      text: 'Automatically categorize and prioritize messages for efficiency.'
    },
    {
      title: 'Keep Sales Flowing',
      text: 'Never miss an opportunity—WAffy ensures seamless communication.'
    }
  ];

  const [current, setCurrent] = useState(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      if (!paused) {
        setCurrent(prev => (prev + 1) % messages.length);
      }
    }, 5000);
    return () => clearInterval(timer);
  }, [paused, messages.length]); // 
  
  
  // const handlePause = () => setPaused(prev => !prev);
  
  return (
    <div className="w-full bg-white overflow-hidden py-16 px-2 sm:px-8">

      <div className="flex flex-col lg:flex-row">
        {/* Left side - Hero slider */}
        <div className="lg:w-3/5 px-8 lg:px-12 flex flex-col justify-center">
          {/* WAffy Logo and Title - left-aligned above headline */}
          <div className="flex items-center mb-10 relative z-10">
            <img src="/logo.png" alt="WAffy Logo" className="h-28 w-auto mr-6 drop-shadow-xl" style={{filter: 'drop-shadow(0 0 18px #f472b6)'}} />
            <div>
              <h1 className="text-5xl lg:text-6xl font-extrabold text-gray-800 leading-tight mb-3">WAffy</h1>
              <p className="text-2xl text-pink-500 font-semibold">Organize WhatsApp Messages, Never Miss a Sale</p>
            </div>
          </div>
          <div
            onMouseEnter={() => setPaused(true)}
            onMouseLeave={() => setPaused(false)}
            className="flex items-center justify-center mt-2">
          <div className="bg-white/80 backdrop-blur rounded-3xl px-12 py-10 shadow-lg border border-gray-100 text-center w-full max-w-3xl min-h-[240px] flex flex-col justify-center items-center transition-all duration-500">
              <div className="text-center">
                <h2 className="text-2xl lg:text-3xl font-bold text-gray-800 mb-4">
                  {messages[current].title}
                </h2>
                <p className="text-lg lg:text-xl text-gray-700">
                  {messages[current].text}
                </p>
              </div>
              <div className="flex justify-center mt-4 space-x-2">
                {messages.map((_, index) => (
                  <span
                    key={index}
                    className={`h-2 w-2 rounded-full transition-all duration-300 ${
                      index === current ? 'bg-pink-500' : 'bg-gray-300'
                    }`}
                  ></span>
                ))}
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap gap-8 mt-12 relative z-10">
            <button
              onClick={() => setActiveTab('signup')}
              className="bg-gradient-to-r from-pink-500 to-yellow-400 text-white font-bold py-4 px-14 rounded-2xl shadow-lg hover:scale-105 hover:shadow-2xl transition-transform duration-300 text-2xl"
            >
              Start Your Free Trial
            </button>
            <button
              onClick={() => setActiveTab('login')}
              className="bg-white text-pink-500 border-2 border-pink-300 font-bold py-4 px-14 rounded-2xl shadow hover:scale-105 hover:shadow-xl transition-transform duration-300 text-2xl"
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

        {/* Right side - Auth forms */}
        <div className="lg:w-2/5 bg-gray-50 p-8 flex flex-col justify-center">
          <div className="flex mb-6 justify-center">
            <button
              className={`flex-1 py-2 text-center border-b-2 ${activeTab === 'login' ? 'border-pink-500 text-pink-500' : 'border-transparent hover:text-pink-500'} focus:outline-none`}
              onClick={() => setActiveTab('login')}
            >
              Login
            </button>
            <button
              className={`flex-1 py-2 text-center border-b-2 ${activeTab === 'signup' ? 'border-pink-500 text-pink-500' : 'border-transparent hover:text-pink-500'} focus:outline-none`}
              onClick={() => setActiveTab('signup')}
            >
              Sign Up
            </button>
          </div>
          <div className="min-h-[600px] overflow-y-auto">
            <div className="w-full flex justify-center">
              {activeTab === 'login' ? <SignIn routing="hash" /> : <SignUp routing="hash" />}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

{/*
<SignedOut>
  <div className="w-full mx-auto p-6">
    <div className="bg-white rounded-xl shadow-xl overflow-hidden">
      <div className="flex flex-col lg:flex-row">
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
          <div className="mt-12">
            <p className="text-sm text-gray-500 mb-4">Integrates with:</p>
            <div className="flex flex-wrap items-center gap-4">
              <span className="bg-gray-100 px-4 py-2 rounded-full text-sm font-medium">WhatsApp Cloud API</span>
              <span className="bg-gray-100 px-4 py-2 rounded-full text-sm font-medium">HubSpot</span>
              <span className="bg-gray-100 px-4 py-2 rounded-full text-sm font-medium">Excel</span>
            </div>
          </div>
        </div>

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
  </div>
</SignedOut>
*/}
