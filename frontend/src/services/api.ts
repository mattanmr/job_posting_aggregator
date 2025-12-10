import axios from "axios";
import {
  JobPosting,
  KeywordResponse,
  CsvFileInfo,
  CollectionStatus,
  ScheduleConfig,
} from "../types";

const base = process.env.REACT_APP_API_URL || "http://localhost:8000";

const apiClient = axios.create({ baseURL: base });

/**
 * Search for jobs
 */
export const searchJobs = async (
  q: string,
  location?: string,
  gl?: string,
  hl?: string,
  page?: number
): Promise<JobPosting[]> => {
  const response = await apiClient.get<JobPosting[]>("/search", {
    params: { q, location, gl: gl || "us", hl: hl || "en", page: page || 1 },
  });
  return response.data;
};

/**
 * Get all configured keywords
 */
export const getKeywords = async (): Promise<string[]> => {
  const response = await apiClient.get<KeywordResponse>("/api/keywords");
  return response.data.keywords;
};

/**
 * Add a new keyword for job collection
 */
export const addKeyword = async (keyword: string): Promise<string[]> => {
  const response = await apiClient.post<KeywordResponse>("/api/keywords", {
    keyword,
  });
  return response.data.keywords;
};

/**
 * Remove a keyword from job collection
 */
export const removeKeyword = async (keyword: string): Promise<string[]> => {
  const response = await apiClient.delete<KeywordResponse>(
    `/api/keywords/${encodeURIComponent(keyword)}`
  );
  return response.data.keywords;
};

/**
 * Get list of all collected CSV files
 */
export const getCsvFiles = async (): Promise<CsvFileInfo[]> => {
  const response = await apiClient.get<CsvFileInfo[]>("/api/csv-files");
  return response.data;
};

/**
 * Download a CSV file
 */
export const downloadCsvFile = async (filename: string): Promise<void> => {
  const response = await apiClient.get(
    `/api/csv-files/${encodeURIComponent(filename)}`,
    {
      responseType: "blob",
    }
  );

  // Create a download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.parentElement?.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Get collection status and next collection time
 */
export const getCollectionStatus = async (): Promise<CollectionStatus> => {
  const response = await apiClient.get<CollectionStatus>(
    "/api/next-collection"
  );
  return response.data;
};

/**
 * Get scheduling configuration
 */
export const getScheduleConfig = async (): Promise<ScheduleConfig> => {
  const response = await apiClient.get<ScheduleConfig>("/api/schedule-config");
  return response.data;
};

/**
 * Update scheduling configuration
 */
export const updateScheduleConfig = async (
  intervalHours: number
): Promise<ScheduleConfig> => {
  const response = await apiClient.put<ScheduleConfig>(
    "/api/schedule-config",
    { interval_hours: intervalHours }
  );
  return response.data;
};

/**
 * Trigger immediate job collection
 */
export const triggerCollectionNow = async (): Promise<{
  status: string;
  message: string;
  total_jobs: number;
  keywords: Array<{
    keyword: string;
    job_count: number;
    filename: string;
  }>;
  timestamp: string;
}> => {
  const response = await apiClient.post("/api/collect-now");
  return response.data;
};

export default apiClient;

