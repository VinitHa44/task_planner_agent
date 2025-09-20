import { PlanCreate, PlanResponse, ApiError } from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
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

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`
        }));
        throw new Error(errorData.detail || 'An error occurred');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Network error occurred');
    }
  }

  // Health check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health');
  }

  // Create a new plan
  async createPlan(planData: PlanCreate): Promise<PlanResponse> {
    return this.request('/plans', {
      method: 'POST',
      body: JSON.stringify(planData),
    });
  }

  // Get all plans
  async getAllPlans(): Promise<PlanResponse[]> {
    return this.request('/plans');
  }

  // Get a specific plan
  async getPlan(planId: string): Promise<PlanResponse> {
    return this.request(`/plans/${planId}`);
  }

  // Update a plan
  async updatePlan(planId: string, planData: Partial<PlanResponse>): Promise<PlanResponse> {
    return this.request(`/plans/${planId}`, {
      method: 'PUT',
      body: JSON.stringify(planData),
    });
  }

  // Delete a plan
  async deletePlan(planId: string): Promise<{ message: string }> {
    return this.request(`/plans/${planId}`, {
      method: 'DELETE',
    });
  }
}

export const apiService = new ApiService();
export default apiService;