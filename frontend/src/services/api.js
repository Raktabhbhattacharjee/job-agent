import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await api.post("/resumes/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return response.data;
};

export const analyzeResume = async (resumeId) => {
  const response = await api.post(`/analysis/${resumeId}`);
  return response.data;
};

export const getAnalysis = async (resumeId) => {
  const response = await api.get(`/analysis/${resumeId}`);
  return response.data;
};

export const scrapeJobs = async (
  tag = "",
  source = "linkedin_india",
  location = "India",
  limit = 15,
) => {
  const params = {
    source,
    location,
    limit,
  };
  if (tag) params.tag = tag;
  const response = await api.post("/jobs/scrape", null, { params });
  return response.data;
};

export const listJobs = async ({
  query = "",
  jobType = "",
  dsaLevel = "",
  experienceLevel = "",
  uniqueCompanies = true,
  skip = 0,
  limit = 50,
} = {}) => {
  const params = { skip, limit };
  if (query) params.query = query;
  if (jobType) params.job_type = jobType;
  if (dsaLevel) params.dsa_level = dsaLevel;
  if (experienceLevel) params.experience_level = experienceLevel;
  params.unique_companies = uniqueCompanies;
  const response = await api.get("/jobs/", { params });
  return response.data;
};

export const getRecommendations = async (
  resumeId,
  limit = 10,
  minScore = 15,
  role = "",
  experienceLevel = "",
) => {
  const response = await api.get(`/recommendations/${resumeId}`, {
    params: {
      limit,
      min_score: minScore,
      ...(role.trim() ? { role: role.trim() } : {}),
      ...(experienceLevel ? { experience_level: experienceLevel } : {}),
    },
  });
  return response.data;
};

export default api;
