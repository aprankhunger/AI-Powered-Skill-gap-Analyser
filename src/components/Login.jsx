import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError("");
  };

  const handleSubmit = e => {
    e.preventDefault();
    if (!form.email.trim() || !form.password.trim()) {
      setError("Please fill out all fields.");
      return;
    }
    // Simulate login success, pass name from email prefix
    const name = form.email.split('@')[0];
    window.dispatchEvent(new CustomEvent("user-login", { detail: name }));
    navigate("/");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#1a2233] to-[#232b3e] pt-24">
      <form onSubmit={handleSubmit} className="bg-white/10 backdrop-blur rounded-2xl p-8 shadow-lg w-full max-w-md border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">Login to SkillGap</h2>
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          className="w-full mb-4 px-4 py-2 rounded-lg bg-black/60 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          className="w-full mb-4 px-4 py-2 rounded-lg bg-black/60 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        {error && <div className="text-red-400 mb-4 text-center font-bold">{error}</div>}
        <button type="submit" className="w-full bg-blue-500 text-white font-bold py-2 rounded-lg hover:bg-blue-600 transition">Login</button>
        <div className="mt-4 text-center text-gray-300">
          Don't have an account? <span className="text-blue-400 cursor-pointer" onClick={() => navigate('/signup')}>Sign Up</span>
        </div>
      </form>
    </div>
  );
}

export default Login;
