import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signup } from "../api/config";

function SignUp() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError("");
  };

  const handleSubmit = async e => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim() || !form.password.trim()) {
      setError("Please fill out all fields.");
      return;
    }
    
    if (form.password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      const response = await signup(form.name, form.email, form.password);
      window.dispatchEvent(new CustomEvent("user-login", { detail: response.user.name }));
      navigate("/");
    } catch (err) {
      setError(err.message || "Sign up failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#1a2233] to-[#232b3e] pt-24">
      <form onSubmit={handleSubmit} className="bg-white/10 backdrop-blur rounded-2xl p-8 shadow-lg w-full max-w-md border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">Sign Up for SkillGap</h2>
        <input
          type="text"
          name="name"
          placeholder="Name"
          value={form.name}
          onChange={handleChange}
          className="w-full mb-4 px-4 py-2 rounded-lg bg-black/60 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
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
        <button 
          type="submit" 
          disabled={loading}
          className={`w-full bg-blue-500 text-white font-bold py-2 rounded-lg transition ${loading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-600'}`}
        >
          {loading ? 'Creating account...' : 'Sign Up'}
        </button>
        <div className="mt-4 text-center text-gray-300">
          Already have an account? <span className="text-blue-400 cursor-pointer" onClick={() => navigate('/login')}>Login</span>
        </div>
      </form>
    </div>
  );
}

export default SignUp;
