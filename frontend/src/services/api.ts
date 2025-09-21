import { PlanCreate, PlanResponse, ApiError } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

class ApiService {
  private async handleResponse<T>(response: Response): Promise<T> {
    console.log('🔄 Frontend API: handleResponse called');
    console.log('📥 Frontend API: Response status:', response.status);
    console.log('📥 Frontend API: Response statusText:', response.statusText);
    console.log('📥 Frontend API: Response headers:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
      console.log('❌ Frontend API: Response not OK');
      let errorData;
      try {
        console.log('🔄 Frontend API: Parsing error response as JSON');
        errorData = await response.json();
        console.log('📤 Frontend API: Parsed error data:', errorData);
      } catch (parseError) {
        console.log('❌ Frontend API: Failed to parse error response as JSON:', parseError);
        // If JSON parsing fails, create a basic error structure
        errorData = {
          error: {
            type: 'HTTP_ERROR',
            message: `HTTP ${response.status}: ${response.statusText}`,
            technical_details: `Request failed with status ${response.status}`
          }
        };
        console.log('📤 Frontend API: Created fallback error data:', errorData);
      }
      
      // If the backend returned a structured error detail, use it
      if (errorData.detail && typeof errorData.detail === 'object' && errorData.detail.error) {
        console.log('🎯 Frontend API: Found structured error in detail');
        console.log('📤 Frontend API: Throwing structured error:', errorData.detail);
        throw errorData.detail;
      }
      
      // If it's a simple string detail, wrap it
      if (typeof errorData.detail === 'string') {
        console.log('🎯 Frontend API: Found string detail, wrapping');
        const wrappedError = {
          error: {
            type: 'HTTP_ERROR',
            message: errorData.detail,
            technical_details: errorData.detail
          }
        };
        console.log('📤 Frontend API: Throwing wrapped error:', wrappedError);
        throw wrappedError;
      }
      
      // If the backend returned a structured error, throw it as is
      if (errorData.error) {
        console.log('🎯 Frontend API: Found direct error object');
        console.log('📤 Frontend API: Throwing direct error:', errorData);
        throw errorData;
      }
      
      // Otherwise, create a structured error
      console.log('🎯 Frontend API: Creating generic error structure');
      const genericError = {
        error: {
          type: 'HTTP_ERROR',
          message: `HTTP ${response.status}: ${response.statusText}`,
          technical_details: JSON.stringify(errorData)
        },
        status: response.status,
        statusText: response.statusText
      };
      console.log('📤 Frontend API: Throwing generic error:', genericError);
      throw genericError;
    }

    try {
      console.log('🔄 Frontend API: Parsing successful response as JSON');
      const result = await response.json();
      console.log('📤 Frontend API: Parsed response data:', result);
      return result;
    } catch (error) {
      console.log('❌ Frontend API: Failed to parse response as JSON:', error);
      const parseError = {
        error: {
          type: 'PARSE_ERROR',
          message: 'Failed to parse server response',
          technical_details: error instanceof Error ? error.message : 'Unknown parsing error'
        }
      };
      console.log('📤 Frontend API: Throwing parse error:', parseError);
      throw parseError;
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    console.log('🔄 Frontend API: request called');
    console.log('📥 Frontend API: URL:', url);
    console.log('📥 Frontend API: Method:', options.method || 'GET');
    console.log('📥 Frontend API: Headers:', options.headers);
    console.log('📥 Frontend API: Body:', options.body);
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    const config: RequestInit = {
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
      ...options,
    };

    console.log('📤 Frontend API: Final config:', config);

    try {
      console.log('🔄 Frontend API: Making fetch request');
      const response = await fetch(url, config);
      console.log('📤 Frontend API: Fetch response received');
      return await this.handleResponse<T>(response);
    } catch (error) {
      console.log('❌ Frontend API: Fetch failed with error:', error);
      // Re-throw structured errors, wrap others
      if (error && typeof error === 'object' && 'error' in error) {
        console.log('🎯 Frontend API: Re-throwing structured error');
        throw error;
      }
      
      console.log('🎯 Frontend API: Wrapping network error');
      const networkError = {
        error: {
          type: 'NETWORK_ERROR',
          message: 'Failed to connect to server. Please check your connection and try again.',
          technical_details: error instanceof Error ? error.message : 'Network request failed'
        }
      };
      console.log('📤 Frontend API: Throwing network error:', networkError);
      throw networkError;
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health');
  }

  // Create a new plan
  async createPlan(planData: PlanCreate): Promise<PlanResponse> {
    try {
      console.log('🔄 Frontend API: createPlan called');
      console.log('📥 Frontend API: Plan data:', planData);
      
      const result = await this.request<PlanResponse>('/api/v1/plans', {
        method: 'POST',
        body: JSON.stringify(planData),
      });
      
      console.log('✅ Frontend API: createPlan completed successfully');
      console.log('📤 Frontend API: Plan created:', result);
      return result;
    } catch (error) {
      console.log('❌ Frontend API: createPlan failed');
      console.log('📥 Frontend API: createPlan error:', error);
      
      // Re-throw structured errors, wrap others
      if (error && typeof error === 'object' && 'error' in error) {
        console.log('🎯 Frontend API: Re-throwing structured createPlan error');
        throw error;
      }
      
      console.log('🎯 Frontend API: Wrapping createPlan error');
      const wrappedError = {
        error: {
          type: 'CREATE_PLAN_ERROR',
          message: 'Failed to create plan. Please try again.',
          technical_details: error instanceof Error ? error.message : 'Plan creation failed'
        }
      };
      console.log('📤 Frontend API: Throwing wrapped createPlan error:', wrappedError);
      throw wrappedError;
    }
  }

  // Get all plans
  async getAllPlans(): Promise<PlanResponse[]> {
    try {
      const response = await this.request<{ plans: PlanResponse[], total: number }>('/api/v1/plans');
      return response.plans;
    } catch (error) {
      if (error && typeof error === 'object' && 'error' in error) {
        throw error;
      }
      
      throw {
        error: {
          type: 'FETCH_PLANS_ERROR',
          message: 'Failed to load plans. Please try again.',
          technical_details: error instanceof Error ? error.message : 'Plans fetch failed'
        }
      };
    }
  }

  // Get a specific plan
  async getPlan(planId: string): Promise<PlanResponse> {
    return this.request(`/api/v1/plans/${planId}`);
  }

  // Update a plan
  async updatePlan(planId: string, planData: Partial<PlanResponse>): Promise<PlanResponse> {
    return this.request(`/api/v1/plans/${planId}`, {
      method: 'PUT',
      body: JSON.stringify(planData),
    });
  }

  // Delete a plan
  async deletePlan(planId: string): Promise<{ message: string }> {
    return this.request(`/api/v1/plans/${planId}`, {
      method: 'DELETE',
    });
  }
}

export const apiService = new ApiService();
export default apiService;