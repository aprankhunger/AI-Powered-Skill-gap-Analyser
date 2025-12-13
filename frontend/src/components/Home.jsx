import React from "react";
import { Suspense, lazy } from 'react';
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  componentDidCatch(error, errorInfo) {
    console.error('Error in 3D Canvas:', error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return <div className="absolute inset-0 -z-10 w-full h-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 text-red-600 text-xl">3D background failed to load.</div>;
    }
    return this.props.children;
  }
}
const Canvas3D = lazy(() => import('./ThreeBackground'));
import { motion } from 'framer-motion';
import { FaSearch, FaRocket, FaBullseye } from 'react-icons/fa';
import { useNavigate, useLocation } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();
  const location = useLocation();
  // Get name from state if redirected from login/signup
  const userName = location.state && location.state.name ? location.state.name : null;
  const handleGetStarted = (e) => {
    e.preventDefault();
    navigate('/scan');
  };
  return (
  <div className="relative min-h-screen flex flex-col items-center justify-center px-4 overflow-hidden bg-transparent pt-32 scroll-smooth font-[Quicksand,sans-serif]">
      {/* Animated particle background */}
      <ErrorBoundary>
        <Suspense fallback={<div className="fixed inset-0 -z-10 w-full h-full bg-gradient-to-br from-[#18181b] via-[#23272f] to-[#0f0f11] flex items-center justify-center text-white text-xl">Loading 3D background...</div>}>
          <Canvas3D />
        </Suspense>
      </ErrorBoundary>
      {/* Background gradient fallback */}
      <div className="fixed inset-0 -z-20 bg-gradient-to-br from-black via-gray-900 to-gray-800"></div>
      {/* Floating hero card */}
      {/* Floating CTA Button */}
      <a href="#" className="fixed bottom-10 right-10 z-40" onClick={handleGetStarted}>
        <motion.span
          whileHover={{ scale: 1.08, boxShadow: "0 0 24px #fff" }}
          whileTap={{ scale: 0.97 }}
          className="bg-white text-black px-8 py-4 rounded-full font-bold shadow-xl text-lg hover:bg-gray-200 transition block"
        >
          Get Started
        </motion.span>
      </a>
  <main className="w-full max-w-5xl mx-auto mt-32 flex flex-col items-center gap-12">
        <motion.div initial={{ y: -40, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 1.2 }} className="w-full bg-white/10 backdrop-blur-2xl rounded-3xl shadow-2xl p-12 flex flex-col items-center justify-center gap-8 border-2 border-white/20">
          <h1 className="text-6xl md:text-7xl font-extrabold text-white drop-shadow-xl tracking-tight mb-4 font-[Quicksand,sans-serif]">
            SkillGap Analyzer{userName ? `, Welcome ${userName}!` : ""}
          </h1>
          <p className="text-2xl text-gray-100 font-semibold mb-6">AI-powered career roadmaps, skill gap analysis, and instant learning plans.</p>
          <motion.button
            whileHover={{ scale: 1.08, boxShadow: "0 0 24px #fff" }}
            whileTap={{ scale: 0.97 }}
            className="bg-white text-black px-10 py-4 rounded-full font-bold shadow-xl text-2xl hover:bg-gray-200 transition"
            onClick={handleGetStarted}
          >
            Get Started
          </motion.button>
        </motion.div>
        {/* Features Section */}
        <section className="w-full max-w-5xl mx-auto mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <motion.div whileHover={{ scale: 1.08, boxShadow: "0 0 24px #fff" }} className="bg-white/10 backdrop-blur-xl rounded-3xl shadow-xl p-8 flex flex-col items-center gap-4 border-2 border-white/20 transition-all duration-300">
            <motion.span animate={{ rotate: [0, 15, -15, 0] }} transition={{ repeat: Infinity, duration: 2 }} className="text-4xl text-white">
              <FaSearch />
            </motion.span>
            <h3 className="text-xl font-bold text-white mb-2">Skill Gap Analysis</h3>
            <p className="text-gray-100">Instantly compare your skills to top jobs and see what you’re missing.</p>
          </motion.div>
          <motion.div whileHover={{ scale: 1.08, boxShadow: "0 0 24px #fff" }} className="bg-white/10 backdrop-blur-xl rounded-3xl shadow-xl p-8 flex flex-col items-center gap-4 border-2 border-white/20 transition-all duration-300">
            <motion.span animate={{ y: [0, -10, 0] }} transition={{ repeat: Infinity, duration: 1.5 }} className="text-4xl text-white">
              <FaRocket />
            </motion.span>
            <h3 className="text-xl font-bold text-white mb-2">Personalized Roadmap</h3>
            <p className="text-gray-100">Get a custom learning plan and resources to close your gaps fast.</p>
          </motion.div>
          <motion.div whileHover={{ scale: 1.08, boxShadow: "0 0 24px #fff" }} className="bg-white/10 backdrop-blur-xl rounded-3xl shadow-xl p-8 flex flex-col items-center gap-4 border-2 border-white/20 transition-all duration-300">
            <motion.span animate={{ scale: [1, 1.2, 1] }} transition={{ repeat: Infinity, duration: 1.2 }} className="text-4xl text-white">
              <FaBullseye />
            </motion.span>
            <h3 className="text-xl font-bold text-white mb-2">Practice Questions</h3>
            <p className="text-gray-100">Auto-generated quizzes to help you master new skills and ace interviews.</p>
          </motion.div>
        </section>
        {/* About Section */}
        <section id="about" className="w-full max-w-4xl mx-auto mt-20 bg-white/10 backdrop-blur-2xl rounded-3xl shadow-2xl border-2 border-white/20 p-12 text-center">
          <h2 className="text-4xl font-extrabold text-white mb-4 font-[Quicksand,sans-serif]">About SkillGap Analyzer</h2>
          <p className="text-gray-100 text-lg">SkillGap Analyzer is an AI-powered platform that helps you bridge your career skill gaps. Upload your resume or LinkedIn, compare with dream jobs, and get a personalized learning roadmap. Built for hackathons, career growth, and wow-factor!</p>
        </section>
      </main>
      {/* Footer */}
      <footer className="w-full max-w-5xl mx-auto mt-20 mb-8 flex flex-col md:flex-row items-center justify-between gap-4 px-4 py-6 bg-white/10 backdrop-blur-2xl rounded-2xl shadow-lg border-2 border-white/20">
        <span className="text-gray-100 text-sm">© {new Date().getFullYear()} SkillGap Analyzer. All rights reserved.</span>
        <div className="flex gap-4">
          <a href="#" className="text-white hover:text-gray-300 transition"><svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M22.46 6c-.77.35-1.6.59-2.47.7a4.3 4.3 0 0 0 1.88-2.37c-.83.5-1.75.87-2.72 1.07A4.28 4.28 0 0 0 12 8.09c0 .34.04.67.1.99C8.09 8.9 4.8 7.13 2.67 4.44c-.37.64-.58 1.38-.58 2.17 0 1.5.77 2.83 1.94 3.61-.72-.02-1.4-.22-1.99-.55v.06c0 2.1 1.49 3.85 3.47 4.25-.36.1-.74.16-1.13.16-.28 0-.54-.03-.8-.08.54 1.7 2.12 2.94 3.99 2.97A8.6 8.6 0 0 1 2 19.54c-.34 0-.67-.02-1-.06A12.13 12.13 0 0 0 7.29 21c7.55 0 11.68-6.26 11.68-11.68 0-.18-.01-.36-.02-.54A8.18 8.18 0 0 0 24 4.59c-.77.34-1.6.58-2.47.7z"/></svg></a>
          <a href="#" className="text-white hover:text-gray-300 transition"><svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.04c-5.5 0-9.96 4.46-9.96 9.96 0 4.41 3.6 8.06 8.01 8.95v-6.34h-2.41v-2.61h2.41V9.41c0-2.39 1.44-3.7 3.64-3.7 1.06 0 2.17.19 2.17.19v2.39h-1.22c-1.2 0-1.57.75-1.57 1.52v1.83h2.67l-.43 2.61h-2.24v6.34c4.41-.89 8.01-4.54 8.01-8.95 0-5.5-4.46-9.96-9.96-9.96z"/></svg></a>
          <a href="#" className="text-white hover:text-gray-300 transition"><svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.04c-5.5 0-9.96 4.46-9.96 9.96 0 4.41 3.6 8.06 8.01 8.95v-6.34h-2.41v-2.61h2.41V9.41c0-2.39 1.44-3.7 3.64-3.7 1.06 0 2.17.19 2.17.19v2.39h-1.22c-1.2 0-1.57.75-1.57 1.52v1.83h2.67l-.43 2.61h-2.24v6.34c4.41-.89 8.01-4.54 8.01-8.95 0-5.5-4.46-9.96-9.96-9.96z"/></svg></a>
        </div>
      </footer>
    </div>
  );
};

export default Home;
