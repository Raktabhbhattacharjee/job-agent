import React, { useState, useEffect } from "react";
import {
  Sparkles,
  Target,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  Loader2,
  Building2,
  MapPin,
  DollarSign,
  ArrowRight,
  User,
  SlidersHorizontal,
} from "lucide-react";
import { getRecommendations } from "../services/api";

export default function Recommendations({
  activeResume,
  analysis,
  onNavigateToUpload,
}) {
  const [recommendations, setRecommendations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [minScore, setMinScore] = useState(15);
  const [manualResumeId, setManualResumeId] = useState(activeResume?.id || "");
  const [role, setRole] = useState("");
  const [experienceLevel, setExperienceLevel] = useState("");

  const fetchRecs = async (resumeId, requestedRole = role) => {
    const id = resumeId || activeResume?.id;
    if (!id) return;

    try {
      setIsLoading(true);
      setError("");
      const data = await getRecommendations(
        id,
        15,
        minScore,
        requestedRole,
        experienceLevel,
      );
      setRecommendations(data.recommendations || []);
    } catch (err) {
      const detail =
        err.response?.data?.detail ||
        err.message ||
        "Failed to fetch recommendations.";
      setError(detail);
      setRecommendations([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeResume?.id) {
      setManualResumeId(activeResume.id);
      fetchRecs(activeResume.id);
    }
  }, [activeResume, minScore, experienceLevel]);

  const handleManualLookup = (e) => {
    e.preventDefault();
    if (manualResumeId) {
      fetchRecs(manualResumeId, role);
    }
  };

  const handlePreferenceSubmit = (e) => {
    e.preventDefault();
    fetchRecs(manualResumeId, role);
  };

  const getScoreBadgeColor = (score) => {
    if (score >= 60) return "bg-emerald-50 text-emerald-700 border-emerald-200";
    if (score >= 40) return "bg-blue-50 text-blue-700 border-blue-200";
    return "bg-amber-50 text-amber-700 border-amber-200";
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            <h2 className="text-xl font-bold text-slate-900">AI Job Matches</h2>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Jobs ranked and matched against your specific candidate skills,
            preferred roles, and projects.
          </p>
        </div>

        {/* Manual ID Input or Active Candidate Tag */}
        <form onSubmit={handleManualLookup} className="flex items-center gap-2">
          <input
            type="number"
            placeholder="Resume ID"
            value={manualResumeId}
            onChange={(e) => setManualResumeId(e.target.value)}
            className="w-28 px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-800 focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={!manualResumeId || isLoading}
            className="px-3.5 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white text-xs font-medium transition-colors"
          >
            {isLoading ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              "Match"
            )}
          </button>
        </form>
      </div>

      {/* Candidate Snapshot Bar */}
      {analysis && (
        <div className="bg-blue-50/70 border border-blue-100 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-blue-600" />
            <span className="font-semibold text-slate-800">
              {analysis.name || "Current Candidate"}
            </span>
            <span className="text-slate-400">|</span>
            <span className="text-slate-600">
              Targeting:{" "}
              {analysis.preferred_roles?.slice(0, 2).join(", ") || "Tech Roles"}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-slate-500">Min Match Score:</span>
            <select
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="px-2 py-1 rounded bg-white border border-blue-200 text-xs font-medium text-slate-800 focus:outline-none"
            >
              <option value="10">10%+</option>
              <option value="20">20%+</option>
              <option value="35">35%+</option>
              <option value="50">50%+</option>
            </select>
          </div>
        </div>
      )}

      <form
        onSubmit={handlePreferenceSubmit}
        className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm"
      >
        <div className="flex items-start gap-3 mb-4">
          <div className="w-9 h-9 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center flex-shrink-0">
            <SlidersHorizontal className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-900">
              What kind of job are you looking for?
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Leave the role blank to use your resume&apos;s recommended roles,
              or type your own.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-[1fr_180px_auto] gap-3 items-end">
          <label className="block">
            <span className="block text-xs font-semibold text-slate-600 mb-1.5">
              Target role
            </span>
            <input
              type="text"
              value={role}
              onChange={(e) => setRole(e.target.value)}
              placeholder={
                analysis?.preferred_roles?.[0] || "e.g. Frontend Developer"
              }
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </label>

          <label className="block">
            <span className="block text-xs font-semibold text-slate-600 mb-1.5">
              Experience
            </span>
            <select
              value={experienceLevel}
              onChange={(e) => setExperienceLevel(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 text-sm text-slate-800 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              <option value="">Any level</option>
              <option value="internship">Internship</option>
              <option value="experienced">Experienced</option>
            </select>
          </label>

          <button
            type="submit"
            disabled={!manualResumeId || isLoading}
            className="inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white text-sm font-semibold transition-colors"
          >
            {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
            Find matches
          </button>
        </div>
      </form>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-xs text-red-700 flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">{error}</p>
            {!activeResume && (
              <button
                onClick={onNavigateToUpload}
                className="mt-2 inline-flex items-center gap-1 font-semibold text-blue-600 hover:underline"
              >
                Go to Resume Upload <ArrowRight className="w-3 h-3" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Empty State when no resume loaded */}
      {!activeResume && !manualResumeId && (
        <div className="py-16 text-center bg-white rounded-xl border border-slate-200 p-8">
          <Target className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h4 className="text-base font-semibold text-slate-800">
            No Resume Analyzed Yet
          </h4>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto mb-4">
            Upload your resume first so the AI agent can extract your skills and
            calculate personalized match scores.
          </p>
          <button
            onClick={onNavigateToUpload}
            className="inline-flex items-center gap-1.5 px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs shadow-sm"
          >
            Upload Resume <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Recommendations List */}
      {isLoading ? (
        <div className="py-20 text-center text-slate-400 flex flex-col items-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-2" />
          <span className="text-xs">
            Evaluating and ranking jobs against your resume...
          </span>
        </div>
      ) : recommendations.length > 0 ? (
        <div className="space-y-4">
          {recommendations.map((rec, idx) => (
            <div
              key={rec.job_id}
              className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow space-y-4"
            >
              {/* Top Row: Title, Company, Match Badge */}
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-400">
                      #{idx + 1}
                    </span>
                    <h3 className="font-semibold text-lg text-slate-900">
                      {rec.title}
                    </h3>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-600 font-medium mt-1">
                    <Building2 className="w-3.5 h-3.5 text-slate-400" />
                    <span>{rec.company}</span>
                    <span className="text-slate-300">•</span>
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span>{rec.location || "Remote"}</span>
                    {rec.salary && (
                      <>
                        <span className="text-slate-300">•</span>
                        <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                        <span className="text-emerald-700 font-semibold">
                          {rec.salary}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                {/* Match Score & DSA Badges */}
                <div className="flex flex-wrap items-center gap-2">
                  {rec.dsa_level && (
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${
                        rec.dsa_level.toLowerCase() === "low"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : rec.dsa_level.toLowerCase() === "heavy"
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : "bg-amber-50 text-amber-700 border-amber-200"
                      }`}
                    >
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          rec.dsa_level.toLowerCase() === "low"
                            ? "bg-emerald-500"
                            : rec.dsa_level.toLowerCase() === "heavy"
                            ? "bg-rose-500"
                            : "bg-amber-500"
                        }`}
                      />
                      {rec.dsa_level} DSA
                    </span>
                  )}
                  <div
                    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${getScoreBadgeColor(rec.match_score)}`}
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{rec.match_score}% Match</span>
                  </div>
                </div>
              </div>

              {/* Fit Reason Box */}
              {rec.fit_reason && (
                <div className="p-3 bg-slate-50 border border-slate-100 rounded-lg text-xs text-slate-700 leading-relaxed">
                  <span className="font-semibold text-slate-900">
                    Why it matches:{" "}
                  </span>
                  {rec.fit_reason}
                </div>
              )}

              {/* Skills Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs pt-1">
                {/* Matched Skills */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-semibold text-emerald-700 uppercase tracking-wider flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Matched Skills (
                    {rec.matched_skills.length})
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {rec.matched_skills.length > 0 ? (
                      rec.matched_skills.map((s, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-800 border border-emerald-200"
                        >
                          {s}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 italic text-[11px]">
                        No direct skill tag overlap
                      </span>
                    )}
                  </div>
                </div>

                {/* Missing Skills */}
                <div className="space-y-1.5">
                  <span className="text-[11px] font-semibold text-amber-700 uppercase tracking-wider flex items-center gap-1">
                    <AlertTriangle className="w-3 h-3" /> Skills to Learn (
                    {rec.missing_skills.length})
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {rec.missing_skills.length > 0 ? (
                      rec.missing_skills.map((s, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-800 border border-amber-200"
                        >
                          {s}
                        </span>
                      ))
                    ) : (
                      <span className="text-slate-400 italic text-[11px]">
                        You meet all required tags!
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Footer / Apply */}
              <div className="pt-3 border-t border-slate-100 flex justify-end">
                <a
                  href={rec.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-colors"
                >
                  Apply on Job Board <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ))}
        </div>
      ) : (
        activeResume &&
        !isLoading && (
          <div className="py-12 text-center bg-white rounded-xl border border-slate-200 p-8">
            <p className="text-sm font-semibold text-slate-800">
              No high matches found for min score of {minScore}%
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Try lowering the minimum score or scraping more jobs in the Job
              Board tab!
            </p>
          </div>
        )
      )}
    </div>
  );
}
