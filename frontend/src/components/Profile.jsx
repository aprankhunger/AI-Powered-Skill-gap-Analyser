import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getProfile, updateProfile, getAnalysisHistory, getLearningProgress, updateLearningProgress, addLearningSkill, deleteLearningProgress } from "../api/config";

function Profile() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [profile, setProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [analyses, setAnalyses] = useState([]);
  const [learningProgress, setLearningProgress] = useState([]);
  const [learningStats, setLearningStats] = useState({});
  const [editMode, setEditMode] = useState(false);
  const [editForm, setEditForm] = useState({});
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    fetchProfileData();
  }, []);

  const fetchProfileData = async () => {
    try {
      setLoading(true);
      const [profileRes, historyRes, learningRes] = await Promise.all([
        getProfile(),
        getAnalysisHistory(),
        getLearningProgress()
      ]);
      
      setProfile(profileRes.profile);
      setStats(profileRes.stats);
      setAnalyses(historyRes.analyses || []);
      setLearningProgress(learningRes.progress || []);
      setLearningStats(learningRes.stats || {});
      setEditForm(profileRes.profile);
    } catch (err) {
      if (err.message?.includes("Not authenticated")) {
        navigate("/login");
      } else {
        setError("Failed to load profile data");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    
    try {
      const response = await updateProfile(editForm);
      setProfile(response.profile);
      setEditMode(false);
      setSuccess("Profile updated successfully!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err) {
      setError(err.message || "Failed to update profile");
    }
  };

  const handleStatusChange = async (progressId, newStatus) => {
    try {
      await updateLearningProgress(progressId, { status: newStatus });
      fetchProfileData();
    } catch (err) {
      setError("Failed to update skill status");
    }
  };

  const handleDeleteSkill = async (progressId) => {
    if (!window.confirm("Remove this skill from your learning list?")) return;
    
    try {
      await deleteLearningProgress(progressId);
      fetchProfileData();
    } catch (err) {
      setError("Failed to remove skill");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#1a2233] to-[#232b3e]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 px-4 pb-12 bg-gradient-to-br from-[#1a2233] to-[#232b3e]">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white/10 backdrop-blur rounded-2xl p-6 shadow-lg border border-white/20 mb-6">
          <div className="flex flex-col md:flex-row items-center gap-6">
            {/* Avatar */}
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-4xl font-bold text-white">
              {profile?.name?.charAt(0).toUpperCase() || "U"}
            </div>
            
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-3xl font-bold text-white">{profile?.name}</h1>
              <p className="text-gray-400">{profile?.email}</p>
              {profile?.current_role && (
                <p className="text-blue-400 mt-1">{profile.current_role}</p>
              )}
              {profile?.target_role && (
                <p className="text-green-400 text-sm">🎯 Target: {profile.target_role}</p>
              )}
            </div>
            
            <button
              onClick={() => setEditMode(!editMode)}
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-full transition"
            >
              {editMode ? "Cancel" : "Edit Profile"}
            </button>
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-500/20 border border-green-500 text-green-300 px-4 py-3 rounded-lg mb-6">
            {success}
          </div>
        )}

        {/* Edit Form */}
        {editMode && (
          <div className="bg-white/10 backdrop-blur rounded-2xl p-6 shadow-lg border border-white/20 mb-6">
            <h2 className="text-xl font-bold text-white mb-4">Edit Profile</h2>
            <form onSubmit={handleUpdateProfile} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-gray-400 text-sm mb-1">Name</label>
                <input
                  type="text"
                  value={editForm.name || ""}
                  onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                  className="w-full px-4 py-2 rounded-lg bg-black/40 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-1">Current Role</label>
                <input
                  type="text"
                  value={editForm.current_role || ""}
                  onChange={(e) => setEditForm({...editForm, current_role: e.target.value})}
                  placeholder="e.g., Junior Developer"
                  className="w-full px-4 py-2 rounded-lg bg-black/40 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-1">Target Role</label>
                <input
                  type="text"
                  value={editForm.target_role || ""}
                  onChange={(e) => setEditForm({...editForm, target_role: e.target.value})}
                  placeholder="e.g., Senior Full Stack Developer"
                  className="w-full px-4 py-2 rounded-lg bg-black/40 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-1">Years of Experience</label>
                <input
                  type="number"
                  value={editForm.years_experience || 0}
                  onChange={(e) => setEditForm({...editForm, years_experience: parseInt(e.target.value)})}
                  className="w-full px-4 py-2 rounded-lg bg-black/40 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-1">LinkedIn URL</label>
                <input
                  type="url"
                  value={editForm.linkedin_url || ""}
                  onChange={(e) => setEditForm({...editForm, linkedin_url: e.target.value})}
                  placeholder="https://linkedin.com/in/..."
                  className="w-full px-4 py-2 rounded-lg bg-black/40 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div>
                <label className="block text-gray-400 text-sm mb-1">GitHub URL</label>
                <input
                  type="url"
                  value={editForm.github_url || ""}
                  onChange={(e) => setEditForm({...editForm, github_url: e.target.value})}
                  placeholder="https://github.com/..."
                  className="w-full px-4 py-2 rounded-lg bg-black/40 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-gray-400 text-sm mb-1">Bio</label>
                <textarea
                  value={editForm.bio || ""}
                  onChange={(e) => setEditForm({...editForm, bio: e.target.value})}
                  rows={3}
                  placeholder="Tell us about yourself..."
                  className="w-full px-4 py-2 rounded-lg bg-black/40 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
              <div className="md:col-span-2">
                <button
                  type="submit"
                  className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-full transition"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20 text-center">
            <div className="text-3xl font-bold text-blue-400">{stats?.total_analyses || 0}</div>
            <div className="text-gray-400 text-sm">Total Analyses</div>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20 text-center">
            <div className="text-3xl font-bold text-green-400">{stats?.avg_skill_match || 0}%</div>
            <div className="text-gray-400 text-sm">Avg Skill Match</div>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20 text-center">
            <div className="text-3xl font-bold text-purple-400">{stats?.avg_ats_score || 0}%</div>
            <div className="text-gray-400 text-sm">Avg ATS Score</div>
          </div>
          <div className="bg-white/10 backdrop-blur rounded-xl p-4 border border-white/20 text-center">
            <div className="text-3xl font-bold text-yellow-400">{stats?.skills_completed || 0}</div>
            <div className="text-gray-400 text-sm">Skills Completed</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto">
          {["overview", "history", "learning"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-2 rounded-full transition whitespace-nowrap ${
                activeTab === tab
                  ? "bg-blue-500 text-white"
                  : "bg-white/10 text-gray-300 hover:bg-white/20"
              }`}
            >
              {tab === "overview" && "📊 Overview"}
              {tab === "history" && "📜 Analysis History"}
              {tab === "learning" && "📚 Learning Progress"}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-white/10 backdrop-blur rounded-2xl p-6 shadow-lg border border-white/20">
          {activeTab === "overview" && (
            <div>
              <h2 className="text-xl font-bold text-white mb-4">Profile Overview</h2>
              
              {profile?.bio && (
                <div className="mb-6">
                  <h3 className="text-gray-400 text-sm mb-2">About</h3>
                  <p className="text-white">{profile.bio}</p>
                </div>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-gray-400 text-sm mb-2">Career Info</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Current Role:</span>
                      <span className="text-white">{profile?.current_role || "Not set"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Target Role:</span>
                      <span className="text-green-400">{profile?.target_role || "Not set"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Experience:</span>
                      <span className="text-white">{profile?.years_experience || 0} years</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-gray-400 text-sm mb-2">Links</h3>
                  <div className="space-y-2">
                    {profile?.linkedin_url && (
                      <a href={profile.linkedin_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-blue-400 hover:underline">
                        <span>🔗</span> LinkedIn
                      </a>
                    )}
                    {profile?.github_url && (
                      <a href={profile.github_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-gray-300 hover:underline">
                        <span>💻</span> GitHub
                      </a>
                    )}
                    {!profile?.linkedin_url && !profile?.github_url && (
                      <p className="text-gray-500">No links added yet</p>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="mt-6 pt-6 border-t border-white/10">
                <h3 className="text-gray-400 text-sm mb-2">Account Info</h3>
                <div className="text-gray-500 text-sm">
                  Member since: {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : "N/A"}
                </div>
              </div>
            </div>
          )}

          {activeTab === "history" && (
            <div>
              <h2 className="text-xl font-bold text-white mb-4">Analysis History</h2>
              
              {analyses.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-400 mb-4">No analyses yet. Upload your resume to get started!</p>
                  <button
                    onClick={() => navigate("/scan")}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-full transition"
                  >
                    Analyze Resume
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {analyses.map((analysis) => (
                    <div
                      key={analysis.id}
                      className="bg-black/20 rounded-xl p-4 border border-white/10 hover:border-white/20 transition cursor-pointer"
                      onClick={() => navigate(`/dashboard`, { 
                        state: { 
                          analysisResult: {
                            analysis: {
                              skill_match_percentage: analysis.skill_match_percentage,
                              ats_score: analysis.ats_score,
                              experience_level: analysis.experience_level,
                              years_of_experience: analysis.years_of_experience,
                              technical_skills: analysis.technical_skills,
                              soft_skills: analysis.soft_skills,
                              missing_skills: analysis.missing_skills,
                              suggestions: analysis.suggestions,
                              learning_resources: analysis.learning_resources,
                              summary: analysis.summary
                            },
                            candidate_info: {
                              name: analysis.candidate_name,
                              email: analysis.candidate_email,
                              phone: analysis.candidate_phone
                            },
                            detected_skills: analysis.technical_skills
                          },
                          fileName: analysis.resume_filename,
                          targetRole: analysis.target_role
                        }
                      })}
                    >
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                        <div>
                          <h3 className="text-white font-semibold">{analysis.target_role}</h3>
                          <p className="text-gray-500 text-sm">{analysis.resume_filename}</p>
                          <p className="text-gray-600 text-xs">
                            {new Date(analysis.created_at).toLocaleDateString()} at {new Date(analysis.created_at).toLocaleTimeString()}
                          </p>
                        </div>
                        <div className="flex gap-4">
                          <div className="text-center">
                            <div className={`text-xl font-bold ${
                              analysis.skill_match_percentage >= 70 ? 'text-green-400' : 
                              analysis.skill_match_percentage >= 50 ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                              {analysis.skill_match_percentage}%
                            </div>
                            <div className="text-gray-500 text-xs">Skill Match</div>
                          </div>
                          <div className="text-center">
                            <div className={`text-xl font-bold ${
                              analysis.ats_score >= 70 ? 'text-green-400' : 
                              analysis.ats_score >= 50 ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                              {analysis.ats_score}%
                            </div>
                            <div className="text-gray-500 text-xs">ATS Score</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === "learning" && (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white">Learning Progress</h2>
                <div className="text-sm text-gray-400">
                  {learningStats.completed || 0} / {learningStats.total || 0} completed
                </div>
              </div>
              
              {learningProgress.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-400 mb-4">No skills being tracked yet.</p>
                  <p className="text-gray-500 text-sm">Skills from your analyses will appear here automatically.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {learningProgress.map((item) => (
                    <div
                      key={item.id}
                      className="bg-black/20 rounded-xl p-4 border border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-3"
                    >
                      <div className="flex-1">
                        <h3 className="text-white font-medium">{item.skill_name}</h3>
                        {item.target_role && (
                          <p className="text-gray-500 text-sm">For: {item.target_role}</p>
                        )}
                        {item.notes && (
                          <p className="text-gray-400 text-sm mt-1">{item.notes}</p>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <select
                          value={item.status}
                          onChange={(e) => handleStatusChange(item.id, e.target.value)}
                          className={`px-3 py-1 rounded-full text-sm font-medium border-0 cursor-pointer ${
                            item.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                            item.status === 'in_progress' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}
                        >
                          <option value="not_started">Not Started</option>
                          <option value="in_progress">In Progress</option>
                          <option value="completed">Completed</option>
                        </select>
                        {item.resource_url && (
                          <a
                            href={item.resource_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full text-sm hover:bg-blue-500/30 transition"
                          >
                            Learn
                          </a>
                        )}
                        <button
                          onClick={() => handleDeleteSkill(item.id)}
                          className="text-red-400 hover:text-red-300 p-1"
                          title="Remove skill"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Profile;
