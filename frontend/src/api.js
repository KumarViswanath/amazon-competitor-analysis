import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minute timeout for competitor analysis operations
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
    return response;
  },
  (error) => {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message;
    console.error(`❌ API Error (${error.response?.status || 'Network'}):`, errorMsg);
    return Promise.reject(error);
  }
);

export const amazonAPI = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Product operations
  scrapeProduct: (productData) => 
    api.post('/api/products/scrape', productData),
  
  getProduct: (asin) => 
    api.get(`/api/products/${asin}`),
  
  searchProducts: (query, limit = 10) => 
    api.get('/api/products/search', { params: { query, limit } }),
  
  getProductStats: () => 
    api.get('/api/products/stats'),

  // Competitor analysis
  analyzeCompetitors: (analysisData) => 
    api.post('/api/competitors/analyze', analysisData),
  
  getCompetitors: (asin) => 
    api.get(`/api/competitors/${asin}`),
  
  getPricingAnalysis: (asin) => 
    api.get(`/api/competitors/${asin}/pricing`),

  // LLM analysis
  analyzeLLM: (llmData) => 
    api.post('/api/llm/analyze', llmData),
};

export default api;