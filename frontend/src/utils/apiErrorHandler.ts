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

// Create error handler function
export const handleApiError = (error: unknown): string => {
  // Handle Axios errors
  if (error instanceof AxiosError) {
    const apiError = error.response?.data as APIError;
    
    // Network error (no response from server)
    if (!error.response) {
      const message = 'Network error. Please check your connection.';
      toast.error(message);
      return message;
    }
    
    // Get the error message from different possible formats
    const errorMessage = apiError?.detail || apiError?.message || 'An error occurred';
    
    // Handle specific status codes
    switch (error.response.status) {
      case 400:
        // Bad Request - validation or duplicate error
        toast.error(errorMessage);
        return errorMessage;
        
      case 404:
        // Not Found
        toast.error(errorMessage);
        return errorMessage;
        
      case 422:
        // Validation Error
        if (apiError?.errors && apiError.errors.length > 0) {
          const firstError = apiError.errors[0];
          const message422 = `${firstError.field}: ${firstError.message}`;
          toast.error(message422);
          return message422;
        }
        toast.error(errorMessage);
        return errorMessage;
        
      case 500:
        // Internal Server Error
        const message500 = 'Server error. Please try again later.';
        toast.error(message500);
        return message500;
        
      default:
        toast.error(errorMessage);
        return errorMessage;
    }
  }
  
  // Handle non-Axios errors
  const genericMessage = 'An unexpected error occurred';
  toast.error(genericMessage);
  return genericMessage;
};

// Create validation error formatter
export const formatValidationErrors = (
  errors: APIError['errors']
): Record<string, string> => {
  if (!errors) return {};
  
  return errors.reduce((acc, error) => {
    // Extract field name (remove 'body -> ' prefix if present)
    const fieldName = error.field.split(' -> ').pop() || error.field;
    acc[fieldName] = error.message;
    return acc;
  }, {} as Record<string, string>);
};

// Create success handler
export const handleApiSuccess = (message: string) => {
  toast.success(message);
};

// Export the APIError type for use in other files
export type { APIError };
