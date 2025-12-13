import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const SkillRoadmap = ({ roadmap, currentMatch, onAddToLearning }) => {
  const [hoveredSkill, setHoveredSkill] = useState(null);
  const [selectedSkill, setSelectedSkill] = useState(null);

  if (!roadmap || roadmap.length === 0) {
    return null;
  }

  // Sort by priority
  const sortedRoadmap = [...roadmap].sort((a, b) => a.priority - b.priority);

  const getImportanceColor = (importance) => {
    switch (importance) {
      case "critical": return { bg: "bg-red-500", border: "border-red-500", text: "text-red-400", glow: "shadow-red-500/50" };
      case "high": return { bg: "bg-orange-500", border: "border-orange-500", text: "text-orange-400", glow: "shadow-orange-500/50" };
      case "medium": return { bg: "bg-yellow-500", border: "border-yellow-500", text: "text-yellow-400", glow: "shadow-yellow-500/50" };
      case "low": return { bg: "bg-green-500", border: "border-green-500", text: "text-green-400", glow: "shadow-green-500/50" };
      default: return { bg: "bg-blue-500", border: "border-blue-500", text: "text-blue-400", glow: "shadow-blue-500/50" };
    }
  };

  const getImportanceLabel = (importance) => {
    switch (importance) {
      case "critical": return "🔴 Critical";
      case "high": return "🟠 High Priority";
      case "medium": return "🟡 Medium";
      case "low": return "🟢 Good to Have";
      default: return "📘 Recommended";
    }
  };

  return (
    <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
      <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
        <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        Your Learning Roadmap
      </h3>
      <p className="text-gray-400 text-sm mb-6">
        Hover over each skill to see why you need it • Click to add to your learning list
      </p>

      {/* Progress indicator */}
      <div className="mb-8 bg-black/30 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-gray-400 text-sm">Current Skill Match</span>
          <span className="text-white font-bold">{currentMatch}%</span>
        </div>
        <div className="relative h-4 bg-gray-700 rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${currentMatch}%` }}
            transition={{ duration: 1, ease: "easeOut" }}
            className="absolute h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full"
          />
          {/* Potential improvement markers */}
          {sortedRoadmap.slice(0, 5).reduce((acc, skill, index) => {
            const prevTotal = acc.prevTotal;
            const newTotal = prevTotal + (skill.improvement_percent || 0);
            acc.markers.push(
              <motion.div
                key={skill.skill}
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.5 }}
                transition={{ delay: 1 + index * 0.2 }}
                className="absolute h-full bg-green-400/30 rounded-full"
                style={{ 
                  left: `${currentMatch + prevTotal}%`, 
                  width: `${skill.improvement_percent || 0}%` 
                }}
              />
            );
            acc.prevTotal = newTotal;
            return acc;
          }, { markers: [], prevTotal: 0 }).markers}
        </div>
        <div className="flex items-center justify-between mt-2">
          <span className="text-gray-500 text-xs">Learn all skills to reach</span>
          <span className="text-green-400 text-sm font-semibold">
            ~{Math.min(100, currentMatch + sortedRoadmap.reduce((sum, s) => sum + (s.improvement_percent || 0), 0))}%
          </span>
        </div>
      </div>

      {/* Roadmap Path */}
      <div className="relative">
        {/* Connecting Line */}
        <div className="absolute left-6 top-8 bottom-8 w-0.5 bg-gradient-to-b from-purple-500 via-blue-500 to-green-500 opacity-30" />
        
        {/* Skill Nodes */}
        <div className="space-y-4">
          {sortedRoadmap.map((skill, index) => {
            const colors = getImportanceColor(skill.importance);
            const isHovered = hoveredSkill === skill.skill;
            const isSelected = selectedSkill === skill.skill;
            
            return (
              <motion.div
                key={skill.skill}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="relative"
              >
                {/* Node */}
                <div
                  className={`relative flex items-start gap-4 p-4 rounded-xl cursor-pointer transition-all duration-300 ${
                    isHovered || isSelected 
                      ? `bg-white/15 border ${colors.border} shadow-lg ${colors.glow}` 
                      : 'bg-black/20 border border-white/10 hover:bg-white/10'
                  }`}
                  onMouseEnter={() => setHoveredSkill(skill.skill)}
                  onMouseLeave={() => setHoveredSkill(null)}
                  onClick={() => setSelectedSkill(isSelected ? null : skill.skill)}
                >
                  {/* Priority Badge */}
                  <div className={`flex-shrink-0 w-12 h-12 rounded-full ${colors.bg} flex items-center justify-center text-white font-bold text-lg shadow-lg relative z-10`}>
                    {skill.priority}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <h4 className="text-white font-semibold text-lg">{skill.skill}</h4>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${colors.bg}/20 ${colors.text}`}>
                        {getImportanceLabel(skill.importance)}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 mt-1 text-sm">
                      <span className="text-green-400 font-medium">
                        +{skill.improvement_percent}% match
                      </span>
                      <span className="text-gray-500">•</span>
                      <span className="text-gray-400">
                        ⏱️ {skill.time_to_learn}
                      </span>
                    </div>

                    {/* Prerequisites */}
                    {skill.prerequisites && skill.prerequisites.length > 0 && (
                      <div className="mt-2 flex items-center gap-2 flex-wrap">
                        <span className="text-gray-500 text-xs">Prerequisites:</span>
                        {skill.prerequisites.map((prereq, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-gray-700 text-gray-300">
                            {prereq}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Expanded Content on Hover/Click */}
                    <AnimatePresence>
                      {(isHovered || isSelected) && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                          className="overflow-hidden"
                        >
                          <div className="mt-4 pt-4 border-t border-white/10">
                            <h5 className="text-gray-300 font-medium mb-2 flex items-center gap-2">
                              <span className="text-yellow-400">💡</span> Why You Need This
                            </h5>
                            <p className="text-gray-400 text-sm leading-relaxed">
                              {skill.reason}
                            </p>
                            
                            <div className="mt-4 flex items-center gap-3">
                              <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onAddToLearning && onAddToLearning(skill);
                                }}
                                className="px-4 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white text-sm font-medium rounded-full hover:shadow-lg transition-shadow"
                              >
                                ➕ Add to Learning List
                              </motion.button>
                              <div className="flex-1 bg-black/30 rounded-full h-2 overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${skill.improvement_percent * 3}%` }}
                                  className="h-full bg-gradient-to-r from-green-400 to-emerald-500"
                                />
                              </div>
                              <span className="text-green-400 text-sm font-bold">
                                +{skill.improvement_percent}%
                              </span>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {/* Arrow indicator */}
                  <div className={`flex-shrink-0 transition-transform duration-300 ${isHovered || isSelected ? 'rotate-90' : ''}`}>
                    <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>

                {/* Connection Line to Next */}
                {index < sortedRoadmap.length - 1 && (
                  <div className="absolute left-[1.45rem] top-full w-0.5 h-4 bg-gradient-to-b from-white/20 to-transparent" />
                )}
              </motion.div>
            );
          })}
        </div>

        {/* End Goal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: sortedRoadmap.length * 0.1 + 0.2 }}
          className="relative mt-6 p-4 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-xl border border-green-500/30"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-gradient-to-r from-green-500 to-emerald-500 flex items-center justify-center text-2xl">
              🎯
            </div>
            <div>
              <h4 className="text-white font-bold">Goal: Job Ready!</h4>
              <p className="text-green-400 text-sm">Complete this roadmap to maximize your chances</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-white/10">
        <p className="text-gray-500 text-xs mb-2">Priority Legend:</p>
        <div className="flex flex-wrap gap-3">
          {[
            { label: "Critical", color: "bg-red-500" },
            { label: "High", color: "bg-orange-500" },
            { label: "Medium", color: "bg-yellow-500" },
            { label: "Good to Have", color: "bg-green-500" },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-1">
              <div className={`w-3 h-3 rounded-full ${item.color}`} />
              <span className="text-gray-400 text-xs">{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SkillRoadmap;
