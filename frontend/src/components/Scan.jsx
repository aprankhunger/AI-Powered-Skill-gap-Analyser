import React, { useState } from "react";


const Scan = () => {

  const [link, setLink] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState("");
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);

  // Simple URL validation
  const isValidUrl = (url) => {
    try {
      new URL(url);
      return true;
    } catch (_) {
      return false;
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!link.trim()) {
      setError("Please enter a link before scanning.");
      setSubmitted(false);
      return;
    }
    if (!isValidUrl(link.trim())) {
      setError("Please enter a valid URL.");
      setSubmitted(false);
      return;
    }
    setError("");
    setSubmitted(true);
    setScanning(true);
    setProgress(0);
    // Simulate scan progress
    let p = 0;
    const interval = setInterval(() => {
      p += Math.floor(Math.random() * 20) + 10;
      if (p >= 100) {
        p = 100;
        setScanning(false);
        clearInterval(interval);
      }
      setProgress(p);
    }, 300);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white px-4">
      <div className="bg-white/10 backdrop-blur-2xl rounded-3xl shadow-2xl p-10 w-full max-w-lg flex flex-col items-center gap-6 border-2 border-white/20">
        <h1 className="text-3xl font-bold mb-4">Paste a Link to Scan</h1>
        <form onSubmit={handleSubmit} className="w-full flex flex-col gap-4">
          <input
            type="text"
            placeholder="Paste any link here..."
            value={link}
            onChange={(e) => { setLink(e.target.value); setError(""); }}
            className="px-4 py-2 rounded-lg bg-black/60 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-white"
          />
          <button type="submit" className="bg-white text-black px-6 py-2 rounded-full font-bold shadow hover:bg-gray-200 transition">Scan</button>
        </form>
        {error && (
          <div className="mt-4 text-red-400 font-bold">{error}</div>
        )}
        {scanning && (
          <div className="w-full mt-4">
            <div className="w-full bg-gray-700 rounded-full h-4">
              <div
                className="bg-green-400 h-4 rounded-full transition-all duration-200"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
            <div className="text-white text-sm mt-2 text-center">Scanning... {progress}%</div>
          </div>
        )}
        {submitted && !error && !scanning && (
          <div className="mt-4 text-green-400">Link submitted for scanning: <span className="break-all">{link}</span></div>
        )}
      </div>
    </div>
  );
};

export default Scan;
