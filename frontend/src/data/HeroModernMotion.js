import React, { useState, useEffect } from 'react';
import { SignedOut, SignIn, SignUp } from '@clerk/clerk-react';


// Modern hero with animated background, animated logo/headline, interactive slider, and button micro-interactions
export default function HeroModernMotion({ activeTab, setActiveTab }) {

  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('signup');
  const [logoAnim, setLogoAnim] = useState(false);
  const [headlineAnim, setHeadlineAnim] = useState(false);
  const [typedTagline, setTypedTagline] = useState('');
  const tagline = 'Let WAffy handle your WhatsApp chats like a smart agent';
  const modalRef = React.useRef(null);

  // Typewriter effect for tagline
  useEffect(() => {
    let i = 0;
    setTypedTagline('');
    const interval = setInterval(() => {
      setTypedTagline((prev) => tagline.slice(0, i + 1));
      i++;
      if (i >= tagline.length) clearInterval(interval);
    }, 24);
    return () => clearInterval(interval);
  }, [showAuthModal]);

  // Animate logo and headline on mount
  useEffect(() => {
    setTimeout(() => setLogoAnim(true), 100);
    setTimeout(() => setHeadlineAnim(true), 400);
  }, []);

  // Modal accessibility: ESC to close, click-outside to close, focus trap
  useEffect(() => {
    if (!showAuthModal) return;
    function onKey(e) {
      if (e.key === 'Escape') setShowAuthModal(false);
    }
    document.addEventListener('keydown', onKey);
    // Focus trap
    const prevActive = document.activeElement;
    if (modalRef.current) modalRef.current.focus();
    return () => {
      document.removeEventListener('keydown', onKey);
      if (prevActive) prevActive.focus();
    };
  }, [showAuthModal]);
  const messages = [
    {
      title: 'WAffy: Your WhatsApp Agent',
      text: 'Handles chats, tags messages, and keeps you focused on what matters.'
    },
    {
      title: 'Smart Chat Tagging',
      text: 'WAffy automatically organizes and prioritizes your WhatsApp conversations.'
    },
    {
      title: 'Automated Replies, Real Results',
      text: 'WAffy responds instantly to customers, so you never miss a sale.'
    }
  ];

  const [current, setCurrent] = useState(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (!paused) {
      const timer = setTimeout(() => setCurrent((c) => (c + 1) % messages.length), 4000);
      return () => clearTimeout(timer);
    }
  }, [current, paused]);

  // Animate logo and headline on mount
  useEffect(() => {
    setTimeout(() => setLogoAnim(true), 100);
    setTimeout(() => setHeadlineAnim(true), 400);
  }, []);

  // Animated gradient background CSS
  // (Tailwind can't animate gradients, so use inline style)
  const bgStyle = {
    background: 'linear-gradient(120deg, #fceabb 0%, #f8bfae 100%)',
    animation: 'gradientMove 8s ease-in-out infinite alternate'
  };

  // Add keyframes to document
  useEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = `@keyframes gradientMove { 0% {background-position:0% 50%;} 100% {background-position:100% 50%;} }`;
    document.head.appendChild(style);
    return () => { document.head.removeChild(style); };
  }, []);

  // Slider manual controls
  const goPrev = () => setCurrent((c) => (c - 1 + messages.length) % messages.length);
  const goNext = () => setCurrent((c) => (c + 1) % messages.length);

  return (
    <div className="relative w-full min-h-[540px] flex items-center justify-center overflow-hidden" style={bgStyle}>
      {/* Authentic WhatsApp-style chat bubbles for hero background */}
      <div className="absolute inset-0 pointer-events-none z-0">
        {/* Outgoing (green) chat bubble */}
        <svg className="absolute left-10 top-16 w-52 h-16 drop-shadow-lg opacity-70 animate-float-slow" viewBox="0 0 220 64" fill="none" style={{zIndex:0}}>
          <path d="M20 8a12 12 0 0 1 12-12h156a12 12 0 0 1 12 12v32a12 12 0 0 1-12 12H60l-28 20 8-20H32A12 12 0 0 1 20 40V8z" fill="#25D366"/>
          <text x="36" y="38" fontSize="18" fill="#fff" fontFamily="sans-serif" opacity="0.85">How can I help?</text>
        </svg>
        {/* Incoming (white) chat bubble */}
        <svg className="absolute right-12 top-32 w-60 h-18 drop-shadow-md opacity-80 animate-float-medium" viewBox="0 0 240 72" fill="none" style={{zIndex:0}}>
          <path d="M220 12a12 12 0 0 0-12-12H32A12 12 0 0 0 20 12v32a12 12 0 0 0 12 12h120l28 16-8-16h24a12 12 0 0 0 12-12V12z" fill="#fff"/>
          <text x="36" y="44" fontSize="18" fill="#222" fontFamily="sans-serif" opacity="0.6">Order confirmed! 👍</text>
        </svg>
        {/* Typing indicator bubble */}
        <svg className="absolute left-1/2 bottom-16 w-36 h-12 drop-shadow opacity-70 animate-float-fast" viewBox="0 0 160 48" fill="none" style={{zIndex:0}}>
          <path d="M20 8a12 12 0 0 1 12-12h96a12 12 0 0 1 12 12v16a12 12 0 0 1-12 12H60l-20 12 6-12H32A12 12 0 0 1 20 24V8z" fill="#e5fbee"/>
          <circle cx="60" cy="28" r="5" fill="#b2dfdb">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" repeatCount="indefinite"/>
          </circle>
          <circle cx="80" cy="28" r="5" fill="#b2dfdb">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" begin="0.4s" repeatCount="indefinite"/>
          </circle>
          <circle cx="100" cy="28" r="5" fill="#b2dfdb">
            <animate attributeName="opacity" values="0.3;1;0.3" dur="1.2s" begin="0.8s" repeatCount="indefinite"/>
          </circle>
        </svg>
      </div>
      <style>{`
        @keyframes float-slow { 0%{transform:translateY(0);} 100%{transform:translateY(-22px);} }
        .animate-float-slow { animation: float-slow 10s ease-in-out infinite alternate; }
        @keyframes float-medium { 0%{transform:translateY(0);} 100%{transform:translateY(-14px);} }
        .animate-float-medium { animation: float-medium 7s ease-in-out infinite alternate; }
        @keyframes float-fast { 0%{transform:translateY(0);} 100%{transform:translateY(-8px);} }
        .animate-float-fast { animation: float-fast 4s ease-in-out infinite alternate; }
      `}</style>
      <div className="relative z-10 w-full max-w-7xl mx-auto flex flex-col lg:flex-row items-center justify-between px-4 py-16">
        {/* Left: Logo & Headline */}
        <div className="flex flex-col items-start lg:w-2/5">
          <div className="flex items-center gap-2 mb-3">
            <img
              src="/transparent.png"
              alt="WAffy Logo"
              className={`h-20 w-auto drop-shadow-xl transition-transform duration-700 ${logoAnim ? 'scale-100 opacity-100' : 'scale-75 opacity-0'} hover:scale-110 animate-bounce-slow`}
              style={{filter: 'drop-shadow(0 0 18px #f472b6)'}}
              onMouseEnter={() => setLogoAnim(true)}
              onMouseLeave={() => setLogoAnim(false)}
            />
            {/* <img src="/assets/whatsapp-bubble.svg" alt="WhatsApp Agent" className="h-10 w-10" /> */}
          </div>
          <h1 className={`text-3xl md:text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight transition-all duration-700 ${headlineAnim ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            WAffy
          </h1>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-green-500 font-semibold text-base md:text-lg tracking-wide">Your WhatsApp Agent</span>
            <span className="inline-flex items-center px-2 py-0.5 rounded bg-green-100 text-green-700 text-xs font-medium">Beta</span>
          </div>
          <p className="text-lg md:text-xl text-pink-500 font-medium mb-5 animate-fade-in min-h-[1.5rem]">
            {typedTagline}
            <span className="inline-block w-2 h-5 align-middle bg-pink-400 animate-pulse ml-1" style={{borderRadius:'2px'}}></span>
          </p>
          <div className="flex flex-wrap gap-4 mt-1">
            <button
              onClick={() => { setShowAuthModal(true); setAuthMode('signup'); }}
              className="bg-gradient-to-r from-pink-500 to-yellow-400 text-white font-bold py-2 px-8 rounded-xl shadow-lg hover:scale-105 hover:shadow-2xl hover:from-yellow-400 hover:to-pink-500 transition-transform duration-300 text-lg focus:ring-4 focus:ring-pink-200"
            >
              Start Your Free Trial
            </button>
            <button
              onClick={() => { setShowAuthModal(true); setAuthMode('login'); }}
              className="bg-white text-pink-500 border-2 border-pink-300 font-bold py-2 px-8 rounded-xl shadow hover:scale-105 hover:shadow-xl transition-transform duration-300 text-lg focus:ring-4 focus:ring-pink-100"
            >
              Login
            </button>
          </div>
          {/* Integration badges */}
          <div className="mt-10">
            <p className="text-sm text-gray-500 mb-4">Integrates with:</p>
            <div className="flex flex-wrap items-center gap-4">
              <span className="bg-gray-100 px-4 py-2 rounded-full text-sm font-medium hover:bg-pink-50 transition cursor-pointer">WhatsApp Cloud API</span>
              <span className="bg-gray-100 px-4 py-2 rounded-full text-sm font-medium hover:bg-yellow-50 transition cursor-pointer">HubSpot</span>
              <span className="bg-gray-100 px-4 py-2 rounded-full text-sm font-medium hover:bg-green-50 transition cursor-pointer">Excel</span>
            </div>
          </div>
        </div>
        {/* Right: Interactive Slider Card */}
        <div className="lg:w-1/2 flex flex-col items-center justify-center mt-12 lg:mt-0">
          <div
            className="relative bg-white/80 backdrop-blur rounded-3xl px-12 py-10 shadow-lg border border-gray-100 text-center w-full max-w-2xl min-h-[240px] flex flex-col justify-center items-center transition-all duration-500 hover:shadow-2xl hover:-translate-y-2 hover:scale-[1.02]"
            onMouseEnter={() => setPaused(true)}
            onMouseLeave={() => setPaused(false)}
          >
            <div className="absolute left-4 top-1/2 -translate-y-1/2">
              <button
                aria-label="Previous"
                className="rounded-full p-2 bg-white shadow hover:bg-pink-100 focus:outline-none focus:ring-2 focus:ring-pink-200 transition"
                onClick={goPrev}
              >
                <svg width="24" height="24" fill="none" stroke="#f472b6" strokeWidth="2" viewBox="0 0 24 24"><path d="M15 19l-7-7 7-7"/></svg>
              </button>
            </div>
            <div className="absolute right-4 top-1/2 -translate-y-1/2">
              <button
                aria-label="Next"
                className="rounded-full p-2 bg-white shadow hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-yellow-200 transition"
                onClick={goNext}
              >
                <svg width="24" height="24" fill="none" stroke="#fbbf24" strokeWidth="2" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>
              </button>
            </div>
            <div className="text-center">
              <h2 className="text-base md:text-lg lg:text-lg font-semibold text-gray-800 mb-2 animate-fade-in">
                {messages[current].title}
              </h2>
              <p className="text-base md:text-lg text-gray-600 mb-1 animate-fade-in">
                {messages[current].text}
              </p>
            </div>
            <div className="flex justify-center gap-2 mt-6">
              {messages.map((_, idx) => (
                <span
                  key={idx}
                  className={`w-4 h-4 rounded-full border-2 transition-all duration-300 ${current === idx ? 'bg-pink-400 border-pink-400 scale-110' : 'bg-white border-gray-300'} cursor-pointer`}
                  onClick={() => setCurrent(idx)}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
      {/* Auth Modal - only show when triggered */}
      {showAuthModal && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center"
          style={{background: 'rgba(0,0,0,0.50)', backdropFilter: 'blur(6px)'}}
          onClick={e => { if (e.target === e.currentTarget) setShowAuthModal(false); }}
        >
          <div
            ref={modalRef}
            tabIndex={-1}
            className={`relative bg-white/80 backdrop-blur-2xl rounded-3xl shadow-2xl p-0 max-w-md w-full border-2 border-green-400 focus:outline-none ${showAuthModal ? 'animate-fade-in-up' : 'animate-fade-out-down'}`}
            role="dialog"
            aria-modal="true"
            style={{boxShadow:'0 8px 40px 0 rgba(40,200,120,0.10), 0 1.5px 24px 0 rgba(0,0,0,0.10)'}}
          >
            {/* Modal header */}
            <div className="flex flex-col items-center pt-8 pb-4 px-8 border-b border-green-100 relative">
              <img src="/logo.png" alt="WAffy Logo" className="h-12 w-auto mb-2 drop-shadow" />
              {/* Animated WhatsApp agent avatar */}
              <h2 className="text-xl font-bold text-gray-900 mb-1 mt-2">Welcome Back</h2>
              <p className="text-green-600 text-sm mb-0.5">Sign in to your WhatsApp Agent</p>
              {/* Typing dots animation */}
              <div className="flex items-center gap-1 mt-1 mb-1 h-3">
                <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-typing-dot" />
                <span className="w-1.5 h-1.5 bg-green-300 rounded-full animate-typing-dot delay-150" />
                <span className="w-1.5 h-1.5 bg-green-200 rounded-full animate-typing-dot delay-300" />
              </div>
              <button
                className="absolute top-3 right-3 text-gray-400 hover:text-green-500 text-2xl font-bold focus:outline-none focus-visible:ring-2 focus-visible:ring-green-400 focus-visible:ring-offset-2 rounded-full px-2 py-1 transition transform-gpu hover:scale-110 hover:rotate-12 active:scale-95 active:bg-green-50 animate-close-btn"
                onClick={() => setShowAuthModal(false)}
                aria-label="Close"
                tabIndex={0}
                onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') setShowAuthModal(false); }}
              >
                &times;
              </button>
            </div>
            {/* Clerk form in branded container */}
            <div className="px-8 py-6 flex flex-col gap-6 items-center justify-center">
              <div className="w-full flex flex-col items-center max-w-xs mx-auto">
                {authMode === 'login' ? <SignIn routing="hash" appearance={{elements:{formButtonPrimary:'bg-green-500 hover:bg-green-600 text-white font-bold', card:'bg-transparent shadow-none border-none', headerTitle:'text-green-600 text-lg font-semibold', footerAction:'text-green-500'}}} /> : <SignUp routing="hash" appearance={{elements:{formButtonPrimary:'bg-green-500 hover:bg-green-600 text-white font-bold', card:'bg-transparent shadow-none border-none', headerTitle:'text-green-600 text-lg font-semibold', footerAction:'text-green-500'}}} />}
              </div>
            </div>
          </div>
          <style>{`
            @keyframes fade-in-up { 0%{opacity:0;transform:translateY(40px);} 100%{opacity:1;transform:translateY(0);} }
            .animate-fade-in-up { animation: fade-in-up 0.5s cubic-bezier(.4,2,.3,1) both; }
            @keyframes fade-out-down { 0%{opacity:1;transform:translateY(0);} 100%{opacity:0;transform:translateY(40px);} }
            .animate-fade-out-down { animation: fade-out-down 0.4s cubic-bezier(.4,2,.3,1) both; }
            @keyframes bounce-once { 0%{transform:translateY(-16px);} 60%{transform:translateY(4px);} 100%{transform:translateY(0);} }
            .animate-bounce-once { animation: bounce-once 1.2s cubic-bezier(.33,1.5,.68,1) 1; }
            @keyframes typing-dot { 0%, 80%, 100% { opacity: 0.3; transform: translateY(0); } 40% { opacity: 1; transform: translateY(-4px); } }
            .animate-typing-dot { animation: typing-dot 1.2s infinite both; }
            .delay-150 { animation-delay: 0.15s; }
            .delay-300 { animation-delay: 0.3s; }
            @keyframes close-btn { 0%{transform:scale(0.8) rotate(-12deg);} 100%{transform:scale(1) rotate(0);} }
            .animate-close-btn { animation: close-btn 0.4s cubic-bezier(.33,1.5,.68,1) 1; }
          `}</style>
        </div>
      )}

    </div>
  );
}
