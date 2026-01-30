import axios from 'axios';

// Environment configuration will be imported once env.ts is created
const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  apiTimeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
  enableApiLogging: import.meta.env.VITE_ENABLE_API_LOGGING === 'true',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
};

// Create axios instance
const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: config.apiTimeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor
apiClient.interceptors.request.use(
  (requestConfig) => {
    // Log request in development
    if (config.enableApiLogging) {
      console.log('🚀 API Request:', {
        method: requestConfig.method?.toUpperCase(),
        url: requestConfig.url,
        data: requestConfig.data,
        params: requestConfig.params,
      });
    }
    

    
    // Add request timestamp for performance tracking
    requestConfig.metadata = { startTime: new Date() };
    
    return requestConfig;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const duration = new Date().getTime() - (response.config.metadata?.startTime?.getTime() || 0);
    
    // Log response in development
    if (config.enableApiLogging) {
      console.log('✅ API Response:', {
        method: response.config.method?.toUpperCase(),
        url: response.config.url,
        status: response.status,
        duration: `${duration}ms`,
        data: response.data,
      });
    }
    
    return response;
  },
  (error) => {
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      console.error('❌ API Error Response:', {
        status: error.response.status,
        url: error.config?.url,
        data: error.response.data,
      });
    } else if (error.request) {
      // Request made but no response received
      console.error('❌ Network Error:', error.message);
    } else {
      // Error in request setup
      console.error('❌ Request Setup Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Export the configured instance
export default apiClient;

// Add TypeScript types for metadata
declare module 'axios' {
  export interface AxiosRequestConfig {
    metadata?: {
      startTime?: Date;
    };
  }
}
