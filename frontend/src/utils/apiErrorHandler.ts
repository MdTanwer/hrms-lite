import { AxiosError } from 'axios';
import toast from 'react-hot-toast';

// Define error response type
interface APIError {
  success?: boolean;
  message?: string;
  detail?: string;
  error_type?: string;
  errors?: Array<{
    field: string;
    message: string;
    type: string;
    input?: any;
    ctx?: any;
  }>;
  error_count?: number;
}

/** Get a user-friendly message from an error without showing a toast. Use in ErrorState etc. */
export const getApiErrorMessage = (error: unknown): string => {
  if (error instanceof AxiosError) {
    const apiError = error.response?.data as APIError;
    if (!error.response) {
      return 'Network error. Please check your connection.';
    }
    const errorMessage = apiError?.detail || apiError?.message || 'An error occurred';
    switch (error.response.status) {
      case 422:
        if (apiError?.errors && apiError.errors.length > 0) {
          const first = apiError.errors[0];
          return `${first.field}: ${first.message}`;
        }
        return errorMessage;
      case 500:
        return errorMessage || 'Server error. Please try again later.';
      default:
        return errorMessage;
    }
  }
  return 'An unexpected error occurred';
};

/** Show toast and return message. Use when you are not rendering a dedicated error UI. */
export const handleApiError = (error: unknown): string => {
  const message = getApiErrorMessage(error);
  toast.error(message);
  return message;
};

export const handleApiSuccess = (message: string) => {
  toast.success(message);
};

export type { APIError };
