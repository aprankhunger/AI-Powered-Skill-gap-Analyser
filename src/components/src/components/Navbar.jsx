import React, { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();
  const [userName, setUserName] = useState("");
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef();

  // Listen for login/signup success via custom event
  React.useEffect(() => {
    const handler = (e) => {
      setUserName(e.detail);
    };
    window.addEventListener("user-login", handler);
    return () => window.removeEventListener("user-login", handler);
  }, []);

  // Close menu on outside click
  React.useEffect(() => {
    function handleClick(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setShowMenu(false);
      }
    }
    if (showMenu) {
      window.addEventListener("mousedown", handleClick);
    }
    return () => window.removeEventListener("mousedown", handleClick);
  }, [showMenu]);

  const handleLogoClick = (e) => {
    e.preventDefault();
    navigate('/');
  };

  const handleLogout = () => {
    setUserName("");
    setShowMenu(false);
  };

  return (
    <nav className="fixed top-0 left-0 w-full z-50 bg-black/80 backdrop-blur-xl shadow-xl py-3 px-6 flex items-center justify-between rounded-b-2xl border-b border-white/10 animate-fade-in">
      <div className="flex items-center gap-4">
        <a href="/" onClick={handleLogoClick} className="cursor-pointer">
          <span className="text-2xl font-extrabold text-white tracking-tight drop-shadow-lg font-[Quicksand,sans-serif]">SkillGap</span>
        </a>
      </div>
      <div className="flex items-center gap-4">
        <a
          href="/about"
          onClick={e => { e.preventDefault(); navigate('/about'); }}
          className="text-white font-medium hover:text-blue-300 transition text-base rounded-full px-3 py-1 hover:bg-white/10"
        >
          About
        </a>
        <a
          href="/blog"
          onClick={e => { e.preventDefault(); navigate('/blog'); }}
          className="text-white font-medium hover:text-blue-300 transition text-base rounded-full px-3 py-1 hover:bg-white/10"
        >
          Blog
        </a>
        <a
          href="/contact"
          onClick={e => { e.preventDefault(); navigate('/contact'); }}
          className="text-white font-medium hover:text-blue-300 transition text-base rounded-full px-3 py-1 hover:bg-white/10"
        >
          Contact
        </a>
        {userName ? (
          <div className="relative" ref={menuRef}>
            <span
              className="text-blue-400 font-semibold text-base ml-4 cursor-pointer hover:underline"
              onClick={() => setShowMenu(v => !v)}
            >
              {userName}
            </span>
            {showMenu && (
              <div className="absolute right-0 mt-2 bg-white rounded shadow-lg py-2 px-4 min-w-[120px] text-black text-sm">
                <button
                  className="w-full text-left px-2 py-1 hover:bg-blue-100 rounded"
                  onClick={handleLogout}
                >
                  Log Out
                </button>
              </div>
            )}
          </div>
        ) : (
          <>
            <a
              href="/login"
              onClick={e => { e.preventDefault(); navigate('/login'); }}
              className="text-blue-400 font-semibold transition text-base rounded-full px-3 py-1 border border-blue-400 hover:bg-blue-400 hover:text-white ml-2"
            >
              Login
            </a>
            <a
              href="/signup"
              onClick={e => { e.preventDefault(); navigate('/signup'); }}
              className="bg-blue-500 text-white font-semibold text-base rounded-full px-4 py-1 ml-2 shadow hover:bg-blue-600 transition"
            >
              Sign Up
            </a>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;


