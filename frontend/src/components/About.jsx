import React from "react";
import { motion } from "framer-motion";
import { FaLinkedin, FaGithub, FaTwitter } from "react-icons/fa";

const team = [
  {
    name: "Ava Patel",
    role: "Founder & AI Architect",
    bio: "Ava leads SkillGap Analyzer's vision and AI engine. She loves hackathons and empowering career growth.",
    img: "https://randomuser.me/api/portraits/women/44.jpg",
    linkedin: "#",
    github: "#",
    twitter: "#"
  },
  {
    name: "Liam Chen",
    role: "Full Stack Developer",
    bio: "Liam builds beautiful, scalable web experiences. He’s passionate about design and user experience.",
    img: "https://randomuser.me/api/portraits/men/32.jpg",
    linkedin: "#",
    github: "#",
    twitter: "#"
  },
  {
    name: "Sofia Garcia",
    role: "Product Designer",
    bio: "Sofia crafts interfaces that delight and inspire. She’s obsessed with glassmorphism and modern UI trends.",
    img: "https://randomuser.me/api/portraits/women/68.jpg",
    linkedin: "#",
    github: "#",
    twitter: "#"
  }
];

const About = () => (
  <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 flex flex-col items-center justify-center px-4 pt-32 font-[Quicksand,sans-serif]">
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
    <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 1.2, delay: 0.3 }} className="w-full max-w-4xl mx-auto bg-white/10 backdrop-blur-2xl rounded-3xl shadow-2xl border-2 border-white/20 p-12 text-center">
      <h2 className="text-4xl font-extrabold text-white mb-8">Meet the Team</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {team.map((member, idx) => (
          <motion.div key={member.name} whileHover={{ scale: 1.05, boxShadow: "0 0 24px #fff" }} className="bg-white/10 rounded-2xl p-8 shadow-xl border border-white/20 flex flex-col items-center transition-all duration-300">
            <img src={member.img} alt={member.name} className="w-24 h-24 rounded-full mb-4 border-4 border-white/30 object-cover" />
            <h3 className="text-xl font-bold text-white mb-1">{member.name}</h3>
            <span className="text-gray-300 mb-2">{member.role}</span>
            <p className="text-gray-100 text-sm mb-4">{member.bio}</p>
            <div className="flex gap-4 mt-2">
              <a href={member.linkedin} className="text-blue-400 hover:text-blue-600" target="_blank" rel="noopener noreferrer"><FaLinkedin size={22} /></a>
              <a href={member.github} className="text-gray-400 hover:text-gray-600" target="_blank" rel="noopener noreferrer"><FaGithub size={22} /></a>
              <a href={member.twitter} className="text-blue-300 hover:text-blue-500" target="_blank" rel="noopener noreferrer"><FaTwitter size={22} /></a>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  </div>
);

export default About;
