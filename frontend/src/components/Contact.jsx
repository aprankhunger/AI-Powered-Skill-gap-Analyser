import React, { useState, useRef } from "react";
import { motion, useInView } from "framer-motion";

const Contact = () => {
  const [form, setForm] = useState({ name: "", email: "", message: "" });
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");
  const formRef = useRef(null);
  const infoRef = useRef(null);
  const formInView = useInView(formRef, { once: true, margin: "-100px" });
  const infoInView = useInView(infoRef, { once: true, margin: "-100px" });

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
    setError("");
  };

  const handleSubmit = e => {
    e.preventDefault();
    if (!form.name.trim() || !form.email.trim() || !form.message.trim()) {
      setError("Please fill out all fields.");
      return;
    }
    // Simple email validation
    if (!/^\S+@\S+\.\S+$/.test(form.email)) {
      setError("Please enter a valid email address.");
      return;
    }
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-gray-800 flex flex-col items-center justify-center px-4 pt-32 font-[Quicksand,sans-serif]">
      {/* Contact Form - scroll animation */}
      <motion.div
        ref={formRef}
        initial={{ opacity: 0, y: 80, scale: 0.95 }}
        animate={formInView ? { opacity: 1, y: 0, scale: 1 } : {}}
        transition={{ duration: 1.1, ease: "easeOut" }}
        className="w-full max-w-xl mx-auto bg-white/10 backdrop-blur-2xl rounded-3xl shadow-2xl border-2 border-white/20 p-12 text-center mb-12"
      >
        <h1 className="text-5xl font-extrabold text-white mb-6">Contact Us</h1>
        <p className="text-gray-100 text-lg mb-6">Have questions, feedback, or partnership ideas? Reach out to the SkillGap Analyzer team below!</p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-6 items-center">
          <input
            type="text"
            name="name"
            placeholder="Your Name"
            value={form.name}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg bg-black/60 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-white"
          />
          <input
            type="email"
            name="email"
            placeholder="Your Email"
            value={form.email}
            onChange={handleChange}
            className="w-full px-4 py-2 rounded-lg bg-black/60 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-white"
          />
          <textarea
            name="message"
            placeholder="Your Message"
            value={form.message}
            onChange={handleChange}
            rows={5}
            className="w-full px-4 py-2 rounded-lg bg-black/60 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-white"
          />
          <motion.button
            whileHover={{ scale: 1.05, boxShadow: "0 0 24px #fff" }}
            whileTap={{ scale: 0.97 }}
            type="submit"
            className="bg-white text-black px-8 py-3 rounded-full font-bold shadow-xl text-lg hover:bg-gray-200 transition block"
          >
            Send Message
          </motion.button>
        </form>
        {error && <div className="mt-4 text-red-400 font-bold">{error}</div>}
        {submitted && !error && (
          <div className="mt-6 text-green-400 text-lg font-bold">Thank you for reaching out! We'll get back to you soon.</div>
        )}
      </motion.div>
      {/* Contact Info Cards - scroll animation */}
      <motion.div
        ref={infoRef}
        initial={{ opacity: 0, y: 80, scale: 0.95 }}
        animate={infoInView ? { opacity: 1, y: 0, scale: 1 } : {}}
        transition={{ duration: 1.1, ease: "easeOut", delay: 0.2 }}
        className="w-full max-w-2xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8"
      >
        <motion.div whileHover={{ scale: 1.04, boxShadow: "0 0 24px #fff" }} className="bg-white/10 rounded-2xl p-8 shadow-xl border border-white/20 flex flex-col items-center transition-all duration-300">
          <h3 className="text-xl font-bold text-white mb-2">General Inquiries</h3>
          <p className="text-gray-100 text-sm mb-2">info@skillgapanalyzer.com</p>
          <p className="text-gray-100 text-sm">+1 (555) 123-4567</p>
        </motion.div>
        <motion.div whileHover={{ scale: 1.04, boxShadow: "0 0 24px #fff" }} className="bg-white/10 rounded-2xl p-8 shadow-xl border border-white/20 flex flex-col items-center transition-all duration-300">
          <h3 className="text-xl font-bold text-white mb-2">Partnerships</h3>
          <p className="text-gray-100 text-sm mb-2">partners@skillgapanalyzer.com</p>
          <p className="text-gray-100 text-sm">Connect with us for collaborations!</p>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Contact;
