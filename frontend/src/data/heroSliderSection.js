import React, { useState, useEffect } from 'react';
import { SignIn, SignUp } from '@clerk/clerk-react';

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
    <div className="bg-white rounded-xl shadow-xl overflow-hidden py-8">
      <div className="flex flex-col lg:flex-row">
        {/* Left side - Hero slider */}
        <div className="lg:w-3/5 px-8 lg:px-12 flex flex-col justify-center">
          <div
            onMouseEnter={() => setPaused(true)}
            onMouseLeave={() => setPaused(false)}
            className="flex items-center justify-center">
          <div className="bg-white/60 backdrop-blur-sm rounded-xl px-8 py-6 shadow-md border border-gray-200 text-center w-full max-w-3xl min-h-[220px] flex flex-col justify-center items-center">
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
          <div className="flex flex-wrap gap-4 mt-8">
            <button
              onClick={() => setActiveTab('signup')}
              className="bg-gradient-to-r from-pink-500 to-yellow-400 text-white font-bold py-3 px-8 rounded-lg shadow-lg hover:shadow-xl transition duration-300"
            >
              Get Started
            </button>
            <button
              onClick={() => setActiveTab('login')}
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
