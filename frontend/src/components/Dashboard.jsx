import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import SkillRoadmap from "./SkillRoadmap";
import { addLearningSkill } from "../api/config";

function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const { analysisResult, fileName, targetRole } = location.state || {};
  const [addedSkills, setAddedSkills] = useState([]);
  const [notification, setNotification] = useState(null);

  // Handle adding skill to learning list
  const handleAddToLearning = async (skill) => {
    try {
      await addLearningSkill({
        skill_name: skill.skill,
        target_role: targetRole,
        resource_url: null,
        notes: `Priority: ${skill.priority} | Expected improvement: +${skill.improvement_percent}%`
      });
      setAddedSkills([...addedSkills, skill.skill]);
      setNotification({ type: 'success', message: `"${skill.skill}" added to your learning list!` });
      setTimeout(() => setNotification(null), 3000);
    } catch (err) {
      if (err.message?.includes("already in your learning")) {
        setNotification({ type: 'info', message: `"${skill.skill}" is already in your learning list` });
      } else if (err.message?.includes("Not authenticated")) {
        setNotification({ type: 'warning', message: 'Please login to save skills to your learning list' });
      } else {
        setNotification({ type: 'error', message: 'Failed to add skill. Please try again.' });
      }
      setTimeout(() => setNotification(null), 3000);
    }
  };

  // If no analysis result, show empty state
  if (!analysisResult) {
    return (
      <div className="min-h-screen pt-24 px-4 bg-gradient-to-br from-[#1a2233] to-[#232b3e]">
        <div className="max-w-2xl mx-auto bg-white/10 backdrop-blur rounded-2xl p-8 shadow-lg border border-white/20 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">No Analysis Data</h2>
          <p className="text-gray-300 mb-6">Upload your resume to get started with skill gap analysis.</p>
          <button 
            onClick={() => navigate('/scan')}
            className="bg-blue-500 text-white font-bold px-6 py-3 rounded-full shadow hover:bg-blue-600 transition"
          >
            Analyze Your Resume
          </button>
        </div>
      </div>
    );
  }

  const { analysis, candidate_info, detected_skills } = analysisResult;

  return (
    <div className="min-h-screen pt-24 px-4 pb-12 bg-gradient-to-br from-[#1a2233] to-[#232b3e]">
      {/* Notification Toast */}
      {notification && (
        <div className={`fixed top-20 right-4 z-50 px-6 py-3 rounded-lg shadow-lg transition-all duration-300 ${
          notification.type === 'success' ? 'bg-green-500 text-white' :
          notification.type === 'error' ? 'bg-red-500 text-white' :
          notification.type === 'warning' ? 'bg-yellow-500 text-black' :
          'bg-blue-500 text-white'
        }`}>
          <div className="flex items-center gap-2">
            {notification.type === 'success' && <span>✅</span>}
            {notification.type === 'error' && <span>❌</span>}
            {notification.type === 'warning' && <span>⚠️</span>}
            {notification.type === 'info' && <span>ℹ️</span>}
            {notification.message}
          </div>
        </div>
      )}

      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white/10 backdrop-blur rounded-2xl p-6 shadow-lg border border-white/20 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-white">
                {candidate_info?.name ? `Welcome, ${candidate_info.name}!` : 'Analysis Results'}
              </h1>
              <p className="text-gray-300 mt-1">Target Role: <span className="text-blue-400 font-semibold">{targetRole}</span></p>
              {fileName && <p className="text-gray-400 text-sm">File: {fileName}</p>}
            </div>
            <button 
              onClick={() => navigate('/scan')}
              className="bg-blue-500 text-white font-bold px-5 py-2 rounded-full shadow hover:bg-blue-600 transition"
            >
              New Analysis
            </button>
          </div>
        </div>

        {/* Score Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <h3 className="text-gray-400 text-sm mb-2">Skill Match</h3>
            <div className="flex items-end gap-2">
              <span className={`text-4xl font-bold ${
                analysis?.skill_match_percentage >= 70 ? 'text-green-400' : 
                analysis?.skill_match_percentage >= 50 ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {analysis?.skill_match_percentage || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 mt-3">
              <div 
                className={`h-2 rounded-full ${
                  analysis?.skill_match_percentage >= 70 ? 'bg-green-400' : 
                  analysis?.skill_match_percentage >= 50 ? 'bg-yellow-400' : 'bg-red-400'
                }`}
                style={{ width: `${analysis?.skill_match_percentage || 0}%` }}
              />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <h3 className="text-gray-400 text-sm mb-2">ATS Score</h3>
            <div className="flex items-end gap-2">
              <span className={`text-4xl font-bold ${
                analysis?.ats_score >= 70 ? 'text-green-400' : 
                analysis?.ats_score >= 50 ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {analysis?.ats_score || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 mt-3">
              <div 
                className={`h-2 rounded-full ${
                  analysis?.ats_score >= 70 ? 'bg-green-400' : 
                  analysis?.ats_score >= 50 ? 'bg-yellow-400' : 'bg-red-400'
                }`}
                style={{ width: `${analysis?.ats_score || 0}%` }}
              />
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <h3 className="text-gray-400 text-sm mb-2">Experience Level</h3>
            <span className="text-2xl font-bold text-purple-400">{analysis?.experience_level || 'N/A'}</span>
            <p className="text-gray-400 text-sm mt-2">{analysis?.years_of_experience || 'Unknown'}</p>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Skills Detected */}
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Technical Skills Found
            </h3>
            <div className="flex flex-wrap gap-2">
              {(analysis?.technical_skills || detected_skills || []).map((skill, i) => (
                <span key={i} className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm border border-green-500/30">
                  {skill}
                </span>
              ))}
              {(!analysis?.technical_skills?.length && !detected_skills?.length) && (
                <p className="text-gray-400">No technical skills detected</p>
              )}
            </div>
            
            {analysis?.soft_skills?.length > 0 && (
              <>
                <h4 className="text-lg font-semibold text-white mt-6 mb-3">Soft Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {analysis.soft_skills.map((skill, i) => (
                    <span key={i} className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm border border-blue-500/30">
                      {skill}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>

          {/* Missing Skills */}
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Skills Gap (Missing Skills)
            </h3>
            <div className="flex flex-wrap gap-2">
              {(analysis?.missing_skills || []).map((skill, i) => (
                <span key={i} className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm border border-red-500/30">
                  {skill}
                </span>
              ))}
              {!analysis?.missing_skills?.length && (
                <p className="text-green-400">Great! No major skill gaps identified!</p>
              )}
            </div>
          </div>

          {/* Skill Roadmap - NEW */}
          {analysis?.skill_roadmap && analysis.skill_roadmap.length > 0 && (
            <div className="lg:col-span-2">
              <SkillRoadmap 
                roadmap={analysis.skill_roadmap}
                currentMatch={analysis.skill_match_percentage || 0}
                onAddToLearning={handleAddToLearning}
              />
            </div>
          )}

          {/* Suggestions */}
          <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20 lg:col-span-2">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              Improvement Suggestions
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {analysis?.suggestions?.ats_optimization?.length > 0 && (
                <div className="bg-black/20 rounded-lg p-4">
                  <h4 className="text-blue-400 font-semibold mb-2">ATS Optimization</h4>
                  <ul className="text-gray-300 text-sm space-y-1">
                    {analysis.suggestions.ats_optimization.map((s, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-blue-400 mt-1">•</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {analysis?.suggestions?.skill_section?.length > 0 && (
                <div className="bg-black/20 rounded-lg p-4">
                  <h4 className="text-purple-400 font-semibold mb-2">Skill Section</h4>
                  <ul className="text-gray-300 text-sm space-y-1">
                    {analysis.suggestions.skill_section.map((s, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-purple-400 mt-1">•</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {analysis?.suggestions?.project_section?.length > 0 && (
                <div className="bg-black/20 rounded-lg p-4">
                  <h4 className="text-green-400 font-semibold mb-2">Project Section</h4>
                  <ul className="text-gray-300 text-sm space-y-1">
                    {analysis.suggestions.project_section.map((s, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-green-400 mt-1">•</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {analysis?.suggestions?.general?.length > 0 && (
                <div className="bg-black/20 rounded-lg p-4">
                  <h4 className="text-yellow-400 font-semibold mb-2">General Tips</h4>
                  <ul className="text-gray-300 text-sm space-y-1">
                    {analysis.suggestions.general.map((s, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-yellow-400 mt-1">•</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

          {/* Learning Resources */}
          {analysis?.learning_resources?.length > 0 && (
            <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20 lg:col-span-2">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/>
                </svg>
                Learning Resources
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analysis.learning_resources.map((resource, i) => (
                  <a 
                    key={i}
                    href={resource.youtube_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-black/20 rounded-lg p-4 hover:bg-black/30 transition border border-white/10 hover:border-red-500/50"
                  >
                    <h4 className="text-white font-semibold mb-2">{resource.skill}</h4>
                    <p className="text-gray-400 text-sm mb-3">{resource.description}</p>
                    <span className="text-red-400 text-sm flex items-center gap-1">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0-3.897.266-4.356 2.62-4.385 8.816.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0 3.897-.266 4.356-2.62 4.385-8.816-.029-6.185-.484-8.549-4.385-8.816zm-10.615 12.816v-8l8 3.993-8 4.007z"/>
                      </svg>
                      Watch on YouTube
                    </span>
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Summary */}
          {analysis?.summary && (
            <div className="bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20 lg:col-span-2">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Summary
              </h3>
              <p className="text-gray-300 leading-relaxed">{analysis.summary}</p>
            </div>
          )}
        </div>

        {/* Contact Info (if available) */}
        {candidate_info && (candidate_info.email || candidate_info.linkedin || candidate_info.github) && (
          <div className="mt-6 bg-white/10 backdrop-blur rounded-xl p-6 border border-white/20">
            <h3 className="text-lg font-bold text-white mb-3">Contact Information Detected</h3>
            <div className="flex flex-wrap gap-4 text-sm">
              {candidate_info.email && (
                <span className="text-gray-300">📧 {candidate_info.email}</span>
              )}
              {candidate_info.phone && (
                <span className="text-gray-300">📱 {candidate_info.phone}</span>
              )}
              {candidate_info.linkedin && (
                <a href={candidate_info.linkedin} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">
                  LinkedIn Profile
                </a>
              )}
              {candidate_info.github && (
                <a href={candidate_info.github} target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:underline">
                  GitHub Profile
                </a>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
