/**
 * Axios API client configuration with interceptors.
 */
import axios from 'axios';
import { ERROR_MESSAGES } from './constants';

// Get CSRF token from cookie
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  withCredentials: true, // Important for session cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add CSRF token to all requests
api.interceptors.request.use(
  (config) => {
    // Add CSRF token for non-GET requests
    if (config.method !== 'get') {
      const csrfToken = getCookie('csrftoken');
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }

    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method.toUpperCase()} ${config.url}`);
    }

    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
api.interceptors.response.use(
  (response) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.method.toUpperCase()} ${response.config.url}`, response.data);
    }

    return response;
  },
  (error) => {
    if (!error.response) {
      // Network error
      console.error('[API Network Error]', error);
      return Promise.reject({
        message: ERROR_MESSAGES.NETWORK_ERROR,
        originalError: error,
      });
    }

    const { status, data } = error.response;

    // Handle specific status codes
    switch (status) {
      case 401:
        // Unauthorized - redirect to login
        console.error('[API 401] Unauthorized');
        window.location.href = '/login';
        return Promise.reject({
          message: ERROR_MESSAGES.UNAUTHORIZED,
          status,
          data,
        });

      case 403:
        // Forbidden
        console.error('[API 403] Forbidden');
        return Promise.reject({
          message: data?.detail || ERROR_MESSAGES.FORBIDDEN,
          status,
          data,
        });

      case 404:
        // Not found
        console.error('[API 404] Not Found');
        return Promise.reject({
          message: data?.detail || ERROR_MESSAGES.NOT_FOUND,
          status,
          data,
        });

      case 500:
      case 502:
      case 503:
        // Server errors
        console.error(`[API ${status}] Server Error`, data);
        return Promise.reject({
          message: ERROR_MESSAGES.SERVER_ERROR,
          status,
          data,
        });

      default:
        // Other errors
        console.error(`[API ${status}] Error`, data);
        return Promise.reject({
          message: data?.detail || data?.message || ERROR_MESSAGES.VALIDATION_ERROR,
          status,
          data,
        });
    }
  }
);

/**
 * Helper function to handle API errors and show toast
 * @param {Error} error - Error object from API call
 * @param {Function} toast - Toast notification function
 */
export const handleApiError = (error, toast) => {
  const message = error?.message || ERROR_MESSAGES.SERVER_ERROR;

  if (toast) {
    toast.error(message);
  }

  // Log error for debugging
  console.error('[API Error Handler]', error);
};

/**
 * Helper function to handle API success and show toast
 * @param {string} message - Success message
 * @param {Function} toast - Toast notification function
 */
export const handleApiSuccess = (message, toast) => {
  if (toast) {
    toast.success(message);
  }
};

export default api;
