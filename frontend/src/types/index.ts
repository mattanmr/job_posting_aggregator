/**
 * TypeScript type definitions for the job posting aggregator
 */

export interface JobPosting {
  id: string;
  title: string;
  company?: string;
  location?: string;
  post_date?: string;
  description?: string;
  url?: string;
  source?: string;
  diploma_required?: string;
  years_experience?: string;
}

export interface KeywordResponse {
  keywords: string[];
}

export interface CsvFileInfo {
  filename: string;
  keyword: string;
  timestamp: string;
  size: number;
  job_count: number;
}

export interface CollectionStatus {
  next_collection_timestamp: string;
  next_collection_time: string;
  last_collection_timestamp?: string;
  last_collection_time?: string;
}
