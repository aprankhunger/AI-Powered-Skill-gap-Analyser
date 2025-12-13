import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzeResume } from "../api/config";

const Scan = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [targetRole, setTargetRole] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState("");
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMessage, setStatusMessage] = useState("");

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile) => {
    setError("");
    if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
      setError("Please upload a PDF file.");
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10MB.");
      return;
    }
    setFile(selectedFile);
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError("Please upload your resume PDF.");
      return;
    }
    
    if (!targetRole.trim()) {
      setError("Please enter your target job role.");
      return;
    }

    setError("");
    setScanning(true);
    setProgress(0);
    setStatusMessage("Uploading resume...");

    // Simulate progress for better UX
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) return prev;
        return prev + Math.random() * 15;
      });
    }, 500);

    try {
      setProgress(30);
      setStatusMessage("Extracting text from PDF...");
      
      setTimeout(() => {
        setProgress(50);
        setStatusMessage("Analyzing skills...");
      }, 1000);

      setTimeout(() => {
        setProgress(70);
        setStatusMessage("Generating recommendations...");
      }, 2000);

      const result = await analyzeResume(file, targetRole);
      
      clearInterval(progressInterval);
      setProgress(100);
      setStatusMessage("Analysis complete!");

      // Navigate to dashboard with results
      setTimeout(() => {
        navigate("/dashboard", { 
          state: { 
            analysisResult: result,
            fileName: file.name,
            targetRole: targetRole
          } 
        });
      }, 500);

    } catch (err) {
      clearInterval(progressInterval);
      setScanning(false);
      setProgress(0);
      setError(err.message || "Failed to analyze resume. Please try again.");
    }
  };

  const removeFile = () => {
    setFile(null);
    setError("");
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-[#1a2233] to-[#232b3e] text-white px-4 pt-20">
      <div className="bg-white/10 backdrop-blur-2xl rounded-3xl shadow-2xl p-10 w-full max-w-lg flex flex-col items-center gap-6 border-2 border-white/20">
        <h1 className="text-3xl font-bold mb-2">Analyze Your Resume</h1>
        <p className="text-gray-300 text-center mb-4">Upload your resume and discover your skill gaps</p>
        
        <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
          {/* File Upload Area */}
          <div
            className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer
              ${dragActive ? 'border-blue-400 bg-blue-400/10' : 'border-white/30 hover:border-white/50'}
              ${file ? 'border-green-400 bg-green-400/10' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => document.getElementById('fileInput').click()}
          >
            <input
              id="fileInput"
              type="file"
              accept=".pdf"
              onChange={handleFileInput}
              className="hidden"
            />
            
            {file ? (
              <div className="flex flex-col items-center gap-2">
                <svg className="w-12 h-12 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-green-400 font-semibold">{file.name}</p>
                <p className="text-gray-400 text-sm">{(file.size / 1024).toFixed(1)} KB</p>
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); removeFile(); }}
                  className="text-red-400 text-sm hover:text-red-300 mt-2"
                >
                  Remove file
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-2">
                <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-gray-300">Drag & drop your resume here</p>
                <p className="text-gray-400 text-sm">or click to browse</p>
                <p className="text-gray-500 text-xs mt-2">PDF only, max 10MB</p>
              </div>
            )}
          </div>

          {/* Target Role Input */}
          <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-300">Target Job Role</label>
            <input
              type="text"
              placeholder="e.g., Full Stack Developer, Data Scientist, Product Manager"
              value={targetRole}
              onChange={(e) => { setTargetRole(e.target.value); setError(""); }}
              className="px-4 py-3 rounded-lg bg-black/60 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-400 placeholder-gray-500"
              disabled={scanning}
            />
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={scanning}
            className={`w-full py-3 rounded-xl font-bold text-lg transition-all
              ${scanning 
                ? 'bg-gray-600 cursor-not-allowed' 
                : 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 shadow-lg hover:shadow-xl'
              }`}
          >
            {scanning ? 'Analyzing...' : 'Analyze Resume'}
          </button>
        </form>

        {/* Error Message */}
        {error && (
          <div className="w-full p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-center">
            {error}
          </div>
        )}

        {/* Progress Bar */}
        {scanning && (
          <div className="w-full mt-2">
            <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-gray-300 text-sm mt-2 text-center">{statusMessage}</p>
          </div>
        )}

        {/* Features */}
        <div className="w-full mt-4 grid grid-cols-3 gap-3 text-center text-xs text-gray-400">
          <div className="flex flex-col items-center gap-1">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span>Secure</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <span>AI Powered</span>
          </div>
          <div className="flex flex-col items-center gap-1">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Fast Analysis</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Scan;
