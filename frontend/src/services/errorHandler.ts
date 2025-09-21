export interface ApiError {
  type: string;
  message: string;
  technical_details?: string;
  retry_after?: number;
}

export interface ApiErrorResponse {
  error: ApiError;
  success: false;
}

export class ErrorHandler {
  static getErrorMessage(error: any): { message: string; type: string; retryAfter?: number } {
    // If it's already a structured error response
    if (error?.error && typeof error.error === 'object') {
      return {
        message: error.error.message || 'An error occurred',
        type: error.error.type || 'UNKNOWN_ERROR',
        retryAfter: error.error.retry_after
      };
    }

    // Handle HTTP status codes
    if (error?.status) {
      switch (error.status) {
        case 400:
          return {
            message: 'Invalid request. Please check your input and try again.',
            type: 'VALIDATION_ERROR'
          };
        case 401:
          return {
            message: 'Authentication failed. Please check your credentials.',
            type: 'AUTH_ERROR'
          };
        case 403:
          return {
            message: 'Access denied. You don\'t have permission to perform this action.',
            type: 'PERMISSION_ERROR'
          };
        case 404:
          return {
            message: 'The requested resource was not found.',
            type: 'NOT_FOUND_ERROR'
          };
        case 429:
          return {
            message: 'Too many requests. Please wait a moment and try again.',
            type: 'RATE_LIMITED'
          };
        case 500:
          return {
            message: 'Server error. Please try again later.',
            type: 'INTERNAL_ERROR'
          };
        case 503:
          return {
            message: 'Service temporarily unavailable. Please try again later.',
            type: 'SERVICE_UNAVAILABLE'
          };
        default:
          return {
            message: `HTTP Error ${error.status}: ${error.statusText || 'Unknown error'}`,
            type: 'HTTP_ERROR'
          };
      }
    }

    // Handle network errors
    if (error?.message) {
      const message = error.message.toLowerCase();
      
      if (message.includes('network') || message.includes('fetch')) {
        return {
          message: 'Network connection issue. Please check your internet and try again.',
          type: 'NETWORK_ERROR'
        };
      }
      
      if (message.includes('timeout')) {
        return {
          message: 'Request timed out. Please try again.',
          type: 'TIMEOUT_ERROR'
        };
      }
      
      if (message.includes('quota') || message.includes('rate limit')) {
        return {
          message: 'AI service quota exceeded. Please try again later.',
          type: 'QUOTA_EXCEEDED'
        };
      }
    }

    // Default fallback
    return {
      message: error?.message || 'An unexpected error occurred. Please try again.',
      type: 'UNKNOWN_ERROR'
    };
  }

  static getErrorIcon(type: string): string {
    switch (type) {
      case 'QUOTA_EXCEEDED':
      case 'RATE_LIMITED':
        return '⏳';
      case 'NETWORK_ERROR':
        return '🌐';
      case 'TIMEOUT_ERROR':
        return '⏰';
      case 'AUTH_ERROR':
      case 'PERMISSION_ERROR':
        return '🔒';
      case 'NOT_FOUND_ERROR':
        return '🔍';
      case 'VALIDATION_ERROR':
        return '⚠️';
      case 'SERVICE_UNAVAILABLE':
        return '🔧';
      case 'INTERNAL_ERROR':
        return '💥';
      default:
        return '❌';
    }
  }

  static shouldShowRetry(type: string): boolean {
    return [
      'QUOTA_EXCEEDED',
      'RATE_LIMITED',
      'NETWORK_ERROR',
      'TIMEOUT_ERROR',
      'SERVICE_UNAVAILABLE',
      'INTERNAL_ERROR'
    ].includes(type);
  }

  static getRetryMessage(retryAfter?: number): string {
    if (retryAfter) {
      const minutes = Math.ceil(retryAfter / 60);
      return `Please try again in ${minutes} minute${minutes > 1 ? 's' : ''}.`;
    }
    return 'Please try again in a few moments.';
  }

  static formatRetryTime(seconds: number): string {
    if (seconds < 60) {
      return `${seconds}s`;
    }
    const minutes = Math.ceil(seconds / 60);
    return `${minutes}m`;
  }
}