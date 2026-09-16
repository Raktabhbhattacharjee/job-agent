import React, { useState } from 'react';
import { Bot, FileText, Briefcase, Sparkles, Github } from 'lucide-react';
import ResumeUpload from './components/ResumeUpload';
import JobBoard from './components/JobBoard';
import Recommendations from './components/Recommendations';

export default function App() {
  const [activeTab, setActiveTab] = useState('resume');
  const [activeResume, setActiveResume] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const handleAnalysisComplete = (resumeData, analysisData) => {
    setActiveResume(resumeData);
    setAnalysis(analysisData);
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-['Inter',sans-serif]">
      {/* Navbar */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          {/* Brand */}
          <div className="flex items-center gap-2.5 cursor-pointer" onClick={() => setActiveTab('resume')}>
            <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/30">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-slate-900 text-base tracking-tight">JobAgent</span>
              <span className="ml-1.5 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                AI Powered
              </span>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200/80 text-xs font-medium">
            <button
              onClick={() => setActiveTab('resume')}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
                activeTab === 'resume'
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Resume & Profile</span>
            </button>

            <button
              onClick={() => setActiveTab('jobs')}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
                activeTab === 'jobs'
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Briefcase className="w-3.5 h-3.5" />
              <span>Job Board</span>
            </button>

            <button
              onClick={() => setActiveTab('recommendations')}
              className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg transition-all ${
                activeTab === 'recommendations'
                  ? 'bg-white text-slate-900 shadow-sm font-semibold'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>Recommendations</span>
              {analysis && (
                <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
              )}
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8">
        {activeTab === 'resume' && (
          <ResumeUpload
            onAnalysisComplete={handleAnalysisComplete}
            activeResume={activeResume}
            analysis={analysis}
          />
        )}

        {activeTab === 'jobs' && <JobBoard />}

        {activeTab === 'recommendations' && (
          <Recommendations
            activeResume={activeResume}
            analysis={analysis}
            onNavigateToUpload={() => setActiveTab('resume')}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-400">
        <p>AI Job Agent • Built with FastAPI, PostgreSQL, Groq (Llama 3.3 70B), Playwright & React</p>
      </footer>
    </div>
  );
}
