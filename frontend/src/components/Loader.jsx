




import { motion } from "framer-motion";

const Loader = () => (
  <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black">
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: [0, 1.2, 1], opacity: [0, 1, 1] }}
      transition={{ duration: 1.2, ease: "easeInOut" }}
      className="flex flex-col items-center"
    >
      <span className="text-white text-5xl font-extrabold mb-4 font-[Quicksand,sans-serif]">SkillGap</span>
      <motion.div
        initial={{ rotate: 0 }}
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
        className="w-16 h-16 border-4 border-white border-t-transparent rounded-full"
      />
    </motion.div>
  </div>
);

export default Loader;
