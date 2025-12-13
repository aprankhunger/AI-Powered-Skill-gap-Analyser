import React from "react";

const posts = [
  {
    title: "How to Identify Your Skill Gaps",
    summary: "Learn how to analyze your current skills and spot gaps for your dream job.",
    date: "August 2025",
    author: "SkillGap Team",
    content: `Step 1: List your current skills.\nStep 2: Compare with job requirements.\nStep 3: Use SkillGap Analyzer to get a gap report.\nStep 4: Prioritize skills to learn next.`
  },
  {
    title: "Top 5 Resources for Upskilling Fast",
    summary: "Discover the best online platforms and courses to boost your skills quickly.",
    date: "August 2025",
    author: "SkillGap Team",
    content: `1. Coursera\n2. Udemy\n3. LinkedIn Learning\n4. edX\n5. SkillGap Analyzer Roadmaps` 
  },
  {
    title: "Career Roadmap: Step-by-Step Guide",
    summary: "A proven roadmap to help you reach your career goals efficiently.",
    date: "August 2025",
    author: "SkillGap Team",
    content: `Step 1: Set your goal.\nStep 2: Map required skills.\nStep 3: Plan learning schedule.\nStep 4: Track progress with SkillGap Analyzer.`
  },
  {
    title: "Mastering Soft Skills for Career Growth",
    summary: "Explore the importance of communication, teamwork, and adaptability in modern workplaces.",
    date: "September 2025",
    author: "SkillGap Team",
    content: `Soft skills are increasingly valued by employers.\n- Communication: Practice active listening and clear expression.\n- Teamwork: Collaborate and support colleagues.\n- Adaptability: Embrace change and learn new tools.\nSkillGap Analyzer can help you assess and improve these skills.`
  },
  {
    title: "Success Stories: Real Users Bridging Skill Gaps",
    summary: "Read inspiring stories from SkillGap Analyzer users who achieved their career goals.",
    date: "September 2025",
    author: "SkillGap Team",
    content: `"I used SkillGap Analyzer to identify missing skills for my dream job. The personalized roadmap helped me focus my learning and land the position!"\n- Priya, Data Analyst\n\n"SkillGap Analyzer made it easy to track my progress and stay motivated."\n- Ahmed, Software Engineer`
  },
  {
    title: "Upcoming Features: What’s Next for SkillGap Analyzer?",
    summary: "A sneak peek at new tools and improvements coming soon to help you upskill faster.",
    date: "September 2025",
    author: "SkillGap Team",
    content: `- AI-powered skill recommendations\n- Community forums for peer support\n- Integration with popular learning platforms\nStay tuned for updates!`
  },
];

function Blog() {
  return (
    <div className="min-h-screen pt-32 pb-16 px-4 bg-gradient-to-br from-[#1a2233] to-[#232b3e]">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-4xl font-extrabold text-white mb-8 text-center">SkillGap Blog & Resources</h1>
        <div className="space-y-8">
          {posts.map((post, idx) => (
            <div key={idx} className="bg-white/10 backdrop-blur rounded-2xl p-6 shadow-lg hover:scale-[1.02] transition-all duration-200 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-2">{post.title}</h2>
              <p className="text-gray-200 mb-2">{post.summary}</p>
              <div className="flex items-center justify-between text-xs text-gray-400 mb-2">
                <span>{post.author}</span>
                <span>{post.date}</span>
              </div>
              <pre className="text-gray-100 bg-black/20 rounded p-4 whitespace-pre-wrap text-sm">{post.content}</pre>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Blog;
