import React, { useState, useEffect } from "react";
import {
  Search,
  Globe,
  ExternalLink,
  RefreshCw,
  Loader2,
  Sparkles,
  Building2,
  MapPin,
  DollarSign,
  Briefcase,
  Users,
  Code2,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Info,
} from "lucide-react";
import { listJobs, scrapeJobs } from "../services/api";

export default function JobBoard() {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState("All");
  const [selectedDsa, setSelectedDsa] = useState("All");
  const [selectedSource, setSelectedSource] = useState("linkedin_india");
  const [locationInput, setLocationInput] = useState("India");
  const [isScraping, setIsScraping] = useState(false);
  const [autoScrape, setAutoScrape] = useState(true);
  const [scrapeStatus, setScrapeStatus] = useState("");
  const [resultCount, setResultCount] = useState(0);
  const [expandedJobs, setExpandedJobs] = useState({});

  const toggleExpand = (jobId) => {
    setExpandedJobs((prev) => ({
      ...prev,
      [jobId]: !prev[jobId],
    }));
  };

  const fetchJobs = async (
    queryOverride = searchQuery,
    typeOverride = selectedType,
    dsaOverride = selectedDsa,
  ) => {
    try {
      setIsLoading(true);
      const data = await listJobs({
        query: queryOverride,
        experienceLevel:
          typeOverride === "All" ? "" : typeOverride.toLowerCase(),
        dsaLevel: dsaOverride === "All" ? "" : dsaOverride,
        limit: 50,
        uniqueCompanies: true,
      });
      setJobs(data);
      setResultCount(data.length);
      return data;
    } catch (err) {
      console.error("Failed to fetch jobs:", err);
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs(searchQuery, selectedType, selectedDsa);
  }, [selectedType, selectedDsa]);

  const handleSearchSubmit = async (e) => {
    e.preventDefault();
    const query = searchQuery.trim();

    if (autoScrape) {
      // Option 1: Live search & scrape
      try {
        setIsScraping(true);
        const sourceName = selectedSource === "linkedin_india" ? "Indian Portals (LinkedIn + Internshala)" : "RemoteOK";
        setScrapeStatus(`Searching and scraping live postings for "${query || 'all roles'}" from ${sourceName}...`);
        const res = await scrapeJobs(query, selectedSource, locationInput, 15);
        const matchingJobs = await fetchJobs(query, selectedType, selectedDsa);
        setScrapeStatus(
          `Scraped ${res.total_saved} fresh postings. Showing ${matchingJobs.length} matching companies.`,
        );
      } catch (err) {
        setScrapeStatus("Failed to scrape live postings. Showing local database matches.");
        fetchJobs(query, selectedType, selectedDsa);
      } finally {
        setIsScraping(false);
      }
    } else {
      // Local database filter only
      fetchJobs(query, selectedType, selectedDsa).then((matchingJobs) => {
        setScrapeStatus(
          `Found ${matchingJobs.length} matching jobs in your database.`,
        );
      });
    }
  };

  const handleTriggerScrape = async () => {
    const query = searchQuery.trim() || (selectedSource === "linkedin_india" ? "python internship" : "python");
    try {
      setIsScraping(true);
      const sourceName = selectedSource === "linkedin_india" ? "LinkedIn India + Internshala" : "RemoteOK";
      setScrapeStatus(`Scraping live internships for "${query}" from ${sourceName} (${locationInput})...`);
      
      const res = await scrapeJobs(query, selectedSource, locationInput, 15);
      const matchingJobs = await fetchJobs(searchQuery, selectedType, selectedDsa);
      setScrapeStatus(
        `Successfully scraped ${res.total_saved} jobs from ${sourceName}. Showing ${matchingJobs.length} matching entries.`,
      );
    } catch (err) {
      setScrapeStatus(
        "Failed to scrape jobs. Try another keyword or check network connection.",
      );
    } finally {
      setIsScraping(false);
    }
  };

  const jobTypes = ["All", "Internship", "Experienced"];
  const dsaLevels = [
    { label: "All DSA", value: "All" },
    { label: "🟢 Low DSA (Dev/Project)", value: "Low" },
    { label: "🟡 Moderate DSA", value: "Moderate" },
    { label: "🔴 Heavy DSA (Algo/LeetCode)", value: "Heavy" },
  ];

  const getDsaBadge = (level) => {
    switch (level?.toLowerCase()) {
      case "low":
        return {
          badge: "bg-emerald-50 text-emerald-700 border-emerald-200",
          dot: "bg-emerald-500",
          text: "Low DSA • Project Focused",
        };
      case "heavy":
        return {
          badge: "bg-rose-50 text-rose-700 border-rose-200",
          dot: "bg-rose-500",
          text: "Heavy DSA • Algo Heavy",
        };
      default:
        return {
          badge: "bg-amber-50 text-amber-700 border-amber-200",
          dot: "bg-amber-500",
          text: "Moderate DSA",
        };
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Search & Scrape Toolbar */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
        {/* Source Selector & Location */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Scraping Source:
            </span>
            <div className="inline-flex p-0.5 rounded-lg bg-slate-100 border border-slate-200 text-xs">
              <button
                type="button"
                onClick={() => setSelectedSource("linkedin_india")}
                className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                  selectedSource === "linkedin_india"
                    ? "bg-white text-blue-700 shadow-sm"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                🇮🇳 India Internships (LinkedIn)
              </button>
              <button
                type="button"
                onClick={() => setSelectedSource("remoteok")}
                className={`px-3 py-1.5 rounded-md font-medium transition-all ${
                  selectedSource === "remoteok"
                    ? "bg-white text-blue-700 shadow-sm"
                    : "text-slate-600 hover:text-slate-900"
                }`}
              >
                🌐 Global Remote (RemoteOK)
              </button>
            </div>
          </div>

          {selectedSource === "linkedin_india" && (
            <div className="flex items-center gap-2">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-xs text-slate-500">Location:</span>
              <input
                type="text"
                value={locationInput}
                onChange={(e) => setLocationInput(e.target.value)}
                placeholder="e.g. India, Bengaluru, Remote"
                className="px-2.5 py-1 text-xs rounded-md border border-slate-200 text-slate-800 focus:outline-none focus:border-blue-500"
              />
            </div>
          )}
        </div>

        {/* Unified Search Input & Scrape Button */}
        <div className="space-y-2">
          <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
            <form onSubmit={handleSearchSubmit} className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder={
                  selectedSource === "linkedin_india"
                    ? "Search or scrape Indian internships (e.g. Python, React, Full Stack, Django)..."
                    : "Search or scrape global remote jobs (e.g. Python, React, DevOps)..."
                }
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-36 py-2.5 rounded-lg border border-slate-200 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={isScraping}
                className="absolute right-1.5 top-1/2 -translate-y-1/2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-slate-900 hover:bg-slate-800 disabled:bg-slate-400 text-white text-xs font-medium transition-colors shadow-xs"
              >
                {isScraping ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : autoScrape ? (
                  <Sparkles className="w-3.5 h-3.5 text-blue-400" />
                ) : (
                  <Search className="w-3.5 h-3.5" />
                )}
                <span>{autoScrape ? "Search & Scrape" : "Search"}</span>
              </button>
            </form>

            <button
              onClick={handleTriggerScrape}
              disabled={isScraping}
              className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white font-medium text-xs sm:text-sm transition-colors shadow-sm shadow-blue-500/20 whitespace-nowrap"
              title="Fetches live postings and analyzes DSA requirements"
            >
              {isScraping ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Globe className="w-4 h-4" />
              )}
              {isScraping ? "Scraping & Analyzing..." : "Scrape Portals"}
            </button>
          </div>

          <div className="flex items-center justify-between px-1 text-xs text-slate-500">
            <label className="inline-flex items-center gap-1.5 cursor-pointer select-none hover:text-slate-700">
              <input
                type="checkbox"
                checked={autoScrape}
                onChange={(e) => setAutoScrape(e.target.checked)}
                className="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-3.5 h-3.5"
              />
              <span className="font-medium">
                Auto-scrape live postings on search (Option 1 enabled)
              </span>
            </label>
            <span className="text-[11px] text-slate-400">
              Sources: LinkedIn India + Internshala
            </span>
          </div>
        </div>

        {/* Filters Row: DSA Requirement & Experience Level */}
        <div className="flex flex-wrap items-center justify-between pt-2 border-t border-slate-100 gap-3">
          {/* DSA Level Filter */}
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs font-medium text-slate-600 mr-1 flex items-center gap-1">
              <Code2 className="w-3.5 h-3.5 text-slate-500" /> DSA Level:
            </span>
            {dsaLevels.map((dsa) => (
              <button
                key={dsa.value}
                onClick={() => setSelectedDsa(dsa.value)}
                className={`px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
                  selectedDsa === dsa.value
                    ? "bg-slate-900 text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {dsa.label}
              </button>
            ))}
          </div>

          {/* Job Type Filter */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-slate-500 mr-1">Role:</span>
            {jobTypes.map((type) => (
              <button
                key={type}
                onClick={() => setSelectedType(type)}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  selectedType === type
                    ? "bg-blue-600 text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {type}
              </button>
            ))}

            <button
              onClick={() => fetchJobs(searchQuery, selectedType, selectedDsa)}
              title="Refresh job list"
              className="ml-2 inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-800 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {scrapeStatus && (
        <div className="text-xs font-medium px-4 py-2.5 rounded-lg bg-blue-50 text-blue-800 border border-blue-200 animate-fadeIn">
          {scrapeStatus}
        </div>
      )}

      {/* Results Header */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <Users className="w-3.5 h-3.5" />
          <span>
            Showing {resultCount} opportunities saved • unique companies
          </span>
        </div>
        {selectedDsa !== "All" && (
          <span className="font-medium text-blue-600">
            Filtered by: {selectedDsa} DSA requirement
          </span>
        )}
      </div>

      {/* Jobs Grid */}
      {isLoading ? (
        <div className="py-20 text-center text-slate-400 flex flex-col items-center">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-2" />
          <span className="text-xs">Loading internships from database...</span>
        </div>
      ) : jobs.length === 0 ? (
        <div className="py-16 text-center bg-white rounded-xl border border-slate-200 p-8">
          <Briefcase className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h4 className="text-base font-semibold text-slate-800">
            No internships found matching your filters
          </h4>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Try resetting the DSA filter or click "Scrape Fresh Internships" above to pull live postings from LinkedIn India.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {jobs.map((job) => {
            const dsaConfig = getDsaBadge(job.dsa_level);
            const isExpanded = !!expandedJobs[job.id];

            return (
              <div
                key={job.id}
                className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between space-y-3"
              >
                <div className="space-y-2.5">
                  {/* Title, Company Avatar, and Experience Badge */}
                  <div className="flex justify-between items-start gap-3">
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-md bg-slate-900 text-white text-[11px] font-bold shadow-xs">
                          {job.company ? job.company.trim().charAt(0).toUpperCase() : "C"}
                        </span>
                        <span className="text-xs font-bold text-slate-800 tracking-wide">
                          {job.company}
                        </span>
                      </div>
                      <h4 className="font-semibold text-base text-slate-900 line-clamp-1">
                        {job.title}
                      </h4>
                    </div>

                    <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-blue-50 text-blue-700 border border-blue-100 flex-shrink-0">
                      {job.job_type || "Internship"}
                    </span>
                  </div>

                  {/* Location and Salary */}
                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                    <span className="flex items-center gap-1 font-medium text-slate-600">
                      <MapPin className="w-3 h-3 text-slate-400" />{" "}
                      {job.location || "India"}
                    </span>
                    {job.salary && (
                      <span className="flex items-center gap-1 font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                        <DollarSign className="w-3 h-3" /> {job.salary}
                      </span>
                    )}
                  </div>

                  {/* DSA Requirement Badge & Rationale */}
                  <div className="space-y-1.5 pt-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${dsaConfig.badge}`}
                      >
                        <span className={`w-1.5 h-1.5 rounded-full ${dsaConfig.dot}`} />
                        {dsaConfig.text}
                      </span>
                    </div>

                    {job.dsa_reason && (
                      <p className="text-[11px] text-slate-500 italic bg-slate-50 px-2.5 py-1.5 rounded-md border border-slate-100">
                        "{job.dsa_reason}"
                      </p>
                    )}
                  </div>

                  {/* Tech Skills Badges */}
                  {job.skills?.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1">
                      {job.skills.slice(0, 5).map((skill, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-700 border border-slate-200/60"
                        >
                          {skill}
                        </span>
                      ))}
                      {job.skills.length > 5 && (
                        <span className="text-[10px] text-slate-400 self-center">
                          +{job.skills.length - 5} more
                        </span>
                      )}
                    </div>
                  )}

                  {/* Company Intel & Expectations Drawer */}
                  {(job.company_intel || (job.expectations && job.expectations.length > 0)) && (
                    <div className="pt-2">
                      <button
                        type="button"
                        onClick={() => toggleExpand(job.id)}
                        className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 hover:text-blue-600 transition-colors"
                      >
                        <Info className="w-3 h-3" />
                        <span>
                          {isExpanded ? "Hide Company Intel" : "What They Build & Expect"}
                        </span>
                        {isExpanded ? (
                          <ChevronUp className="w-3 h-3" />
                        ) : (
                          <ChevronDown className="w-3 h-3" />
                        )}
                      </button>

                      {isExpanded && (
                        <div className="mt-2 p-3 bg-slate-50 rounded-lg border border-slate-200/80 space-y-2.5 text-xs animate-fadeIn">
                          {job.company_intel && (
                            <div>
                              <span className="font-semibold text-slate-700 text-[11px] uppercase tracking-wider block mb-0.5">
                                What the company builds:
                              </span>
                              <p className="text-slate-600 leading-relaxed">
                                {job.company_intel}
                              </p>
                            </div>
                          )}

                          {job.expectations?.length > 0 && (
                            <div>
                              <span className="font-semibold text-slate-700 text-[11px] uppercase tracking-wider block mb-1">
                                Intern expectations:
                              </span>
                              <ul className="space-y-1">
                                {job.expectations.map((exp, idx) => (
                                  <li
                                    key={idx}
                                    className="flex items-start gap-1.5 text-slate-600"
                                  >
                                    <CheckCircle2 className="w-3 h-3 text-emerald-600 mt-0.5 flex-shrink-0" />
                                    <span>{exp}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Footer: Source + Apply Button */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400 font-medium">
                    {job.source === "linkedin_india"
                      ? "Via LinkedIn India"
                      : job.source === "internshala"
                      ? "Via Internshala"
                      : "Via RemoteOK"}
                  </span>

                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-md bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold transition-colors"
                  >
                    Apply on{" "}
                    {job.source === "linkedin_india"
                      ? "LinkedIn"
                      : job.source === "internshala"
                      ? "Internshala"
                      : "RemoteOK"}{" "}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
