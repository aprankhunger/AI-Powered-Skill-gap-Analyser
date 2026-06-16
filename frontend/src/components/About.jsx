import React from "react";
import { motion } from "framer-motion";
import { FaLinkedin, FaInstagram, FaEnvelope } from "react-icons/fa";
import { HiCode, HiServer, HiDatabase, HiCog, HiDocumentText, HiClipboardCheck, HiLightningBolt } from "react-icons/hi";

const responsibilities = [
  { icon: <HiLightningBolt className="text-yellow-400" size={22} />, label: "Project Planning & Architecture" },
  { icon: <HiCode className="text-cyan-400" size={22} />, label: "Frontend Development" },
  { icon: <HiServer className="text-purple-400" size={22} />, label: "Backend Development" },
  { icon: <HiDatabase className="text-green-400" size={22} />, label: "Database Design & Management" },
  { icon: <HiCog className="text-orange-400" size={22} />, label: "API Integration" },
  { icon: <HiClipboardCheck className="text-pink-400" size={22} />, label: "Testing & Deployment" },
  { icon: <HiDocumentText className="text-blue-400" size={22} />, label: "Documentation & Maintenance" },
];

const About = () => (
  <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 flex flex-col items-center justify-center px-4 pt-32 pb-16 font-[Quicksand,sans-serif]">
    {/* About the Project */}
    <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1.2 }} className="w-full max-w-4xl mx-auto bg-white/10 backdrop-blur-2xl rounded-3xl shadow-2xl border-2 border-white/20 p-12 mb-12 text-center">
      <h1 className="text-5xl font-extrabold text-white mb-6">About SkillGap Analyzer</h1>
      <p className="text-gray-100 text-lg mb-6">SkillGap Analyzer is an AI-powered platform that helps you bridge your career skill gaps. Upload your resume or LinkedIn, compare with dream jobs, and get a personalized learning roadmap. Built for hackathons, career growth, and wow-factor!</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
        <div className="bg-white/10 rounded-2xl p-6 shadow-xl border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-2">Our Mission</h2>
          <p className="text-gray-100">Empower everyone to reach their dream career by making skill gaps visible and actionable.</p>
        </div>
        <div className="bg-white/10 rounded-2xl p-6 shadow-xl border border-white/20">
          <h2 className="text-2xl font-bold text-white mb-2">Why SkillGap?</h2>
          <p className="text-gray-100">We use AI to analyze your skills, match you to top jobs, and create instant learning plans tailored just for you.</p>
        </div>
      </div>
    </motion.div>

    {/* Developer Profile */}
    <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1.2, delay: 0.3 }} className="w-full max-w-4xl mx-auto bg-white/10 backdrop-blur-2xl rounded-3xl shadow-2xl border-2 border-white/20 p-12 text-center">
      <h2 className="text-4xl font-extrabold text-white mb-10">Meet the Developer</h2>
      <div className="flex flex-col items-center">
        {/* Avatar with gradient ring */}
        <motion.div
          whileHover={{ scale: 1.08, boxShadow: "0 0 40px rgba(99,102,241,0.5)" }}
          className="w-36 h-36 rounded-full mb-6 border-4 border-transparent bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-1 shadow-2xl"
        >
          <div className="w-full h-full rounded-full bg-gray-900 flex items-center justify-center text-5xl font-extrabold text-white select-none">
            AK
          </div>
        </motion.div>

        <h3 className="text-3xl font-bold text-white mb-1">Apran Khunger</h3>
        <span className="text-lg text-indigo-300 font-semibold mb-4">Founder & Developer</span>

        <p className="text-gray-100 text-base max-w-2xl leading-relaxed mb-8">
          Passionate Computer Science student focused on software development, Artificial Intelligence, and problem-solving. Responsible for the complete design, development, testing, and deployment of this project. Experienced in web development, IoT systems, and machine learning projects, with a strong interest in building practical solutions that solve real-world problems.
        </p>

        {/* Responsibilities */}
        <div className="w-full max-w-xl mb-8">
          <h4 className="text-xl font-bold text-white mb-4">Responsibilities</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {responsibilities.map((item, idx) => (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.5 + idx * 0.1 }}
                className="flex items-center gap-3 bg-white/5 rounded-xl px-4 py-3 border border-white/10 hover:bg-white/10 transition-all duration-200"
              >
                {item.icon}
                <span className="text-gray-100 text-sm font-medium">{item.label}</span>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Quote */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.2, delay: 1.2 }}
          className="bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20 rounded-2xl px-8 py-5 border border-white/10 max-w-lg mb-6"
        >
          <p className="text-white italic text-lg font-medium">
            "Building impactful technology through continuous learning and innovation."
          </p>
        </motion.div>

        {/* Social Links */}
        <div className="flex gap-5 mt-2">
          <a href="https://www.linkedin.com/in/apran-khunger-6a5234325/" className="text-blue-400 hover:text-blue-300 transition-colors duration-200" target="_blank" rel="noopener noreferrer"><FaLinkedin size={26} /></a>
          <a href="http://instagram.com/apran_khunger" className="text-pink-400 hover:text-pink-300 transition-colors duration-200" target="_blank" rel="noopener noreferrer"><FaInstagram size={26} /></a>
          <a href="mailto:apranofficial@gmail.com" className="text-red-400 hover:text-red-300 transition-colors duration-200"><FaEnvelope size={26} /></a>
        </div>
      </div>
    </motion.div>
  </div>
);

export default About;

