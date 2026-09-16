import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, Sparkles, User, Mail, Phone, Briefcase, GraduationCap, FolderGit2 } from 'lucide-react';
import { uploadResume, analyzeResume } from '../services/api';

export default function ResumeUpload({ onAnalysisComplete, activeResume, analysis }) {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [dragOver, setDragOver] = useState(false);

  const handleFileDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    setError('');
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      if (droppedFile.type !== 'application/pdf' && !droppedFile.name.endsWith('.pdf')) {
        setError('Only PDF resumes are supported. Please convert your file to PDF.');
        return;
      }
      setFile(droppedFile);
    }
  };

  const handleFileSelect = (e) => {
    setError('');
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf' && !selectedFile.name.endsWith('.pdf')) {
        setError('Only PDF resumes are supported. Please convert your file to PDF.');
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleProcessResume = async () => {
    if (!file) {
      setError('Please choose a PDF file first.');
      return;
    }

    try {
      setError('');
      setIsUploading(true);

      // 1. Upload to backend
      const resumeResult = await uploadResume(file);

      setIsUploading(false);
      setIsAnalyzing(true);

      // 2. Trigger Groq LLM analysis
      const analysisResult = await analyzeResume(resumeResult.id);
      setIsAnalyzing(false);

      if (onAnalysisComplete) {
        onAnalysisComplete(resumeResult, analysisResult);
      }
    } catch (err) {
      setIsUploading(false);
      setIsAnalyzing(false);
      const detail = err.response?.data?.detail || err.message || 'Something went wrong processing your resume.';
      setError(detail);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Upload Box Card */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8">
        <div className="text-center max-w-xl mx-auto mb-6">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-50 text-blue-600 mb-3">
            <Upload className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900">Upload Your Resume</h2>
          <p className="text-sm text-slate-500 mt-1">
            Upload your PDF resume. Our AI agent will extract your skills, past projects, and target roles to match you with live jobs.
          </p>
        </div>

        {/* Drop Zone */}
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleFileDrop}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${
            dragOver ? 'border-blue-500 bg-blue-50/50' : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
          }`}
          onClick={() => document.getElementById('resume-file-input').click()}
        >
          <input
            id="resume-file-input"
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileSelect}
            className="hidden"
          />

          {file ? (
            <div className="flex flex-col items-center">
              <FileText className="w-12 h-12 text-blue-600 mb-2" />
              <span className="font-medium text-slate-800">{file.name}</span>
              <span className="text-xs text-slate-500 mt-0.5">({(file.size / 1024).toFixed(1)} KB)</span>
              <span className="text-xs text-blue-600 font-medium mt-2">Click or drop to replace</span>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <Upload className="w-10 h-10 text-slate-400 mb-2" />
              <p className="text-sm font-medium text-slate-700">Drag & drop your PDF here, or <span className="text-blue-600 underline">browse</span></p>
              <p className="text-xs text-slate-400 mt-1">PDF format only (Max 10MB)</p>
            </div>
          )}
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-sm text-red-700">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleProcessResume}
            disabled={!file || isUploading || isAnalyzing}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-medium text-sm transition-all shadow-sm shadow-blue-500/20"
          >
            {isUploading && <Loader2 className="w-4 h-4 animate-spin" />}
            {isAnalyzing && <Sparkles className="w-4 h-4 animate-spin text-yellow-300" />}
            {isUploading ? 'Uploading Resume...' : isAnalyzing ? 'AI Analyzing Profile...' : 'Analyze Resume'}
          </button>
        </div>
      </div>

      {/* Profile Analysis Result Display */}
      {analysis && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6 animate-fadeIn">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-100 gap-4">
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-2xl font-bold text-slate-900">{analysis.name || 'Candidate Profile'}</h3>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <CheckCircle2 className="w-3 h-3" /> Analyzed
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500 mt-2">
                {analysis.email && (
                  <span className="flex items-center gap-1"><Mail className="w-3.5 h-3.5" /> {analysis.email}</span>
                )}
                {analysis.phone && (
                  <span className="flex items-center gap-1"><Phone className="w-3.5 h-3.5" /> {analysis.phone}</span>
                )}
                {activeResume?.filename && (
                  <span className="flex items-center gap-1"><FileText className="w-3.5 h-3.5" /> {activeResume.filename}</span>
                )}
              </div>
            </div>
          </div>

          {/* Professional Summary */}
          {analysis.summary && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Professional Summary</h4>
              <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100">
                {analysis.summary}
              </p>
            </div>
          )}

          {/* Target / Preferred Roles */}
          {analysis.preferred_roles?.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Briefcase className="w-3.5 h-3.5" /> Recommended Target Roles
              </h4>
              <div className="flex flex-wrap gap-2">
                {analysis.preferred_roles.map((role, i) => (
                  <span key={i} className="px-3 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
                    {role}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Extracted Skills */}
          {analysis.skills?.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> Extracted Skills & Technologies
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {analysis.skills.map((skill, i) => (
                  <span key={i} className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-100 text-slate-800 border border-slate-200">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Projects & Experience Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            {/* Experience */}
            {analysis.experience?.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5" /> Experience
                </h4>
                <div className="space-y-3">
                  {analysis.experience.map((exp, i) => (
                    <div key={i} className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/50">
                      <div className="flex justify-between items-start">
                        <span className="font-semibold text-sm text-slate-900">{exp.role}</span>
                        <span className="text-xs text-slate-400">{exp.duration}</span>
                      </div>
                      <p className="text-xs text-slate-600 mt-0.5">{exp.company}</p>
                      {exp.highlights?.length > 0 && (
                        <ul className="mt-2 space-y-1 text-xs text-slate-500 list-disc list-inside">
                          {exp.highlights.slice(0, 2).map((h, j) => (
                            <li key={j}>{h}</li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Projects */}
            {analysis.projects?.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <FolderGit2 className="w-3.5 h-3.5" /> Key Projects
                </h4>
                <div className="space-y-3">
                  {analysis.projects.map((proj, i) => (
                    <div key={i} className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/50">
                      <span className="font-semibold text-sm text-slate-900">{proj.title}</span>
                      <p className="text-xs text-slate-600 mt-1">{proj.description}</p>
                      {proj.technologies?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {proj.technologies.map((t, j) => (
                            <span key={j} className="px-1.5 py-0.5 rounded text-[10px] bg-slate-200/70 text-slate-700">
                              {t}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
