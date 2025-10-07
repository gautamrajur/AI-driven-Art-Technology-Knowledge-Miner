import axios from 'axios';
import { z } from 'zod';

// API base URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response schemas
const SearchResultSchema = z.object({
  content: z.string(),
  title: z.string(),
  url: z.string(),
  domain: z.string(),
  publish_date: z.string().optional(),
  relevance_score: z.number(),
  chunk_index: z.number(),
  total_chunks: z.number(),
});

const SearchResponseSchema = z.object({
  query: z.string(),
  results: z.array(SearchResultSchema),
  total_results: z.number(),
});

const TrendDataSchema = z.object({
  time_period: z.string(),
  count: z.number(),
  trend_slope: z.number().optional(),
  trend_significance: z.number().optional(),
  r_squared: z.number().optional(),
});

const CooccurrenceDataSchema = z.object({
  tag1: z.string(),
  tag2: z.string(),
  count: z.number(),
  correlation: z.number().optional(),
});

const TrendsResponseSchema = z.object({
  facet: z.string(),
  trends: z.array(TrendDataSchema),
  cooccurrence: z.array(CooccurrenceDataSchema),
});

const IngestResponseSchema = z.object({
  task_id: z.string(),
  status: z.string(),
  message: z.string(),
});

const TaskStatusSchema = z.object({
  task_id: z.string(),
  status: z.string(),
  progress: z.number().optional(),
  message: z.string().optional(),
  result: z.any().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

const HealthResponseSchema = z.object({
  status: z.string(),
  services: z.record(z.boolean()),
  database: z.boolean(),
  version: z.string(),
});

const StatsResponseSchema = z.object({
  total_chunks: z.number(),
  total_documents: z.number(),
  collection_name: z.string(),
  embedding_model: z.string(),
  unique_domains: z.number(),
  date_range: z.object({
    min: z.string().optional(),
    max: z.string().optional(),
  }),
});

// API functions
export const apiService = {
  // Search
  search: async (query: string, nResults: number = 10, hybrid: boolean = true) => {
    const response = await api.get('/search', {
      params: { q: query, n_results: nResults, hybrid },
    });
    return SearchResponseSchema.parse(response.data);
  },

  // Trends
  getTrends: async (
    facet: string = 'all',
    fromDate?: string,
    toDate?: string,
    granularity: string = 'year',
    minCooccurrence: number = 2
  ) => {
    const response = await api.get('/trends', {
      params: {
        facet,
        from_date: fromDate,
        to_date: toDate,
        granularity,
        min_cooccurrence: minCooccurrence,
      },
    });
    return TrendsResponseSchema.parse(response.data);
  },

  // Ingest
  ingest: async (queries: string[], maxPages: number = 10) => {
    const response = await api.post('/ingest', {
      queries,
      max_pages: maxPages,
    });
    return IngestResponseSchema.parse(response.data);
  },

  getIngestionStatus: async (taskId: string) => {
    const response = await api.get(`/ingest/${taskId}/status`);
    return TaskStatusSchema.parse(response.data);
  },

  // Health and stats
  getHealth: async () => {
    const response = await api.get('/healthz');
    return HealthResponseSchema.parse(response.data);
  },

  getStats: async () => {
    const response = await api.get('/stats');
    return StatsResponseSchema.parse(response.data);
  },
};

// Error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;
