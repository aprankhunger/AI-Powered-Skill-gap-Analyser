import React from "react";
import { useLocation } from "react-router-dom";

function Dashboard() {
  const location = useLocation();
  const userName = location.state && location.state.name ? location.state.name : null;
  return (
    <div className="min-h-screen pt-24 px-4 bg-gradient-to-br from-[#1a2233] to-[#232b3e]">
      <div className="max-w-2xl mx-auto bg-white/10 backdrop-blur rounded-2xl p-8 shadow-lg border border-white/20">
        <h2 className="text-3xl font-bold text-white mb-4 text-center">
          {userName ? `Welcome, ${userName}!` : "Welcome to Your Dashboard!"}
        </h2>
        <p className="text-gray-200 text-lg mb-6 text-center">Here you can view your personalized career roadmap, track your skill gaps, and access exclusive resources.</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-black/30 rounded-xl p-6 text-white shadow border border-white/10">
            <h3 className="font-bold text-xl mb-2">Skill Gap Analysis</h3>
            <p className="text-gray-300">See how your skills compare to top jobs and get suggestions for improvement.</p>
          </div>
          <div className="bg-black/30 rounded-xl p-6 text-white shadow border border-white/10">
            <h3 className="font-bold text-xl mb-2">Personalized Roadmap</h3>
            <p className="text-gray-300">View your custom learning plan and track your progress.</p>
          </div>
        </div>
        <div className="mt-8 text-center">
          <button className="bg-blue-500 text-white font-bold px-6 py-2 rounded-full shadow hover:bg-blue-600 transition">Explore More Features</button>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
