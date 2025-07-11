// frontend/services/agentService.ts
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  RecommendationRequest,
  RecommendationResponse,
  AgentFeedback,
  PerformanceMetrics,
  HealthStatus,
  UserContext
} from '../types/agents';

class AgentService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.api = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30 second timeout for agent processing
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for auth
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('Agent Service Error:', error);

        if (error.response?.status === 401) {
          // Handle authentication errors
          this.handleAuthError();
        }

        return Promise.reject(this.formatError(error));
      }
    );
  }

  /**
   * Get recommendations from the agent orchestrator
   */
  async getRecommendations(request: RecommendationRequest): Promise<RecommendationResponse> {
    try {
      const response: AxiosResponse<RecommendationResponse> = await this.api.post(
        '/api/v1/agents/recommendations',
        request
      );

      return response.data;
    } catch (error) {
      throw new Error(`Failed to get recommendations: ${error}`);
    }
  }

  /**
   * Submit feedback to improve agent performance
   */
  async submitFeedback(feedback: AgentFeedback): Promise<boolean> {
    try {
      const response: AxiosResponse<{ success: boolean }> = await this.api.post(
        '/api/v1/agents/feedback',
        feedback
      );

      return response.data.success;
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      return false; // Don't throw error for feedback failures
    }
  }

  /**
   * Get agent performance metrics
   */
  async getPerformanceMetrics(userId: string): Promise<PerformanceMetrics> {
    try {
      const response: AxiosResponse<PerformanceMetrics> = await this.api.get(
        `/api/v1/agents/performance/${userId}`
      );

      return response.data;
    } catch (error) {
      throw new Error(`Failed to get performance metrics: ${error}`);
    }
  }

  /**
   * Check health status of all agents
   */
  async getHealthStatus(): Promise<HealthStatus> {
    try {
      const response: AxiosResponse<HealthStatus> = await this.api.get(
        '/api/v1/agents/health'
      );

      return response.data;
    } catch (error) {
      throw new Error(`Failed to get health status: ${error}`);
    }
  }

  /**
   * Quick reorder suggestions based on user history
   */
  async getQuickReorder(userContext: UserContext): Promise<RecommendationResponse> {
    const quickRequest: RecommendationRequest = {
      user_context: userContext,
      request_type: 'quick_recommendation'
    };

    return this.getRecommendations(quickRequest);
  }

  /**
   * Assess delivery risk for a specific order
   */
  async assessDeliveryRisk(
    userContext: UserContext,
    orderDetails: any
  ): Promise<RecommendationResponse> {
    const riskRequest: RecommendationRequest = {
      user_context: userContext,
      request_type: 'risk_assessment',
      order_details: orderDetails
    };

    return this.getRecommendations(riskRequest);
  }

  /**
   * Get contextual information only (for app startup)
   */
  async getContextualInfo(userContext: UserContext): Promise<RecommendationResponse> {
    const contextRequest: RecommendationRequest = {
      user_context: userContext,
      request_type: 'context_only'
    };

    return this.getRecommendations(contextRequest);
  }

  /**
   * Report order outcome for agent learning
   */
  async reportOrderOutcome(
    userId: string,
    orderId: string,
    outcome: {
      delivered_on_time: boolean;
      actual_delivery_time: number;
      predicted_delivery_time: number;
      customer_satisfaction: number;
      problems_encountered: string[];
      agent_recommendations_used: string[];
    }
  ): Promise<boolean> {
    try {
      await this.api.post('/api/v1/agents/order-outcome', {
        user_id: userId,
        order_id: orderId,
        ...outcome
      });

      return true;
    } catch (error) {
      console.error('Failed to report order outcome:', error);
      return false;
    }
  }

  /**
   * Submit experiment data (for research purposes)
   */
  async submitExperimentData(
    experimentId: string,
    trialData: {
      user_id: string;
      trial_type: 'baseline' | 'adaptive';
      start_time: string;
      end_time: string;
      task_completion_time: number;
      nasa_tlx_scores: Record<string, number>;
      sus_score: number;
      user_satisfaction: number;
      recommendations_accepted: number;
      errors_made: number;
      navigation_steps: number;
    }
  ): Promise<boolean> {
    try {
      await this.api.post('/api/v1/experiments/trial-data', {
        experiment_id: experimentId,
        ...trialData
      });

      return true;
    } catch (error) {
      console.error('Failed to submit experiment data:', error);
      return false;
    }
  }

  /**
   * Get user's ordering patterns summary
   */
  async getUserPatterns(userId: string): Promise<any> {
    try {
      const response = await this.api.get(`/api/v1/users/${userId}/patterns`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get user patterns: ${error}`);
    }
  }

  /**
   * Update user preferences manually
   */
  async updateUserPreferences(
    userId: string,
    preferences: {
      dietary_restrictions?: string[];
      favorite_cuisines?: string[];
      price_range?: { min: number; max: number };
      delivery_preferences?: Record<string, any>;
    }
  ): Promise<boolean> {
    try {
      await this.api.put(`/api/v1/users/${userId}/preferences`, preferences);
      return true;
    } catch (error) {
      console.error('Failed to update user preferences:', error);
      return false;
    }
  }

  /**
   * Handle authentication errors
   */
  private handleAuthError(): void {
    localStorage.removeItem('auth_token');
    // Redirect to login or trigger auth refresh
    window.location.href = '/login';
  }

  /**
   * Format error messages consistently
   */
  private formatError(error: any): Error {
    if (error.response?.data?.message) {
      return new Error(error.response.data.message);
    }

    if (error.response?.data?.detail) {
      return new Error(error.response.data.detail);
    }

    if (error.message) {
      return new Error(error.message);
    }

    return new Error('An unexpected error occurred');
  }
}

// Create singleton instance
export const agentService = new AgentService();

// React hook for using the agent service
import { useCallback } from 'react';

export const useAgentService = () => {
  const getRecommendations = useCallback(
    (request: RecommendationRequest) => agentService.getRecommendations(request),
    []
  );

  const submitFeedback = useCallback(
    (feedback: AgentFeedback) => agentService.submitFeedback(feedback),
    []
  );

  const getQuickReorder = useCallback(
    (userContext: UserContext) => agentService.getQuickReorder(userContext),
    []
  );

  const assessDeliveryRisk = useCallback(
    (userContext: UserContext, orderDetails: any) =>
      agentService.assessDeliveryRisk(userContext, orderDetails),
    []
  );

  const getContextualInfo = useCallback(
    (userContext: UserContext) => agentService.getContextualInfo(userContext),
    []
  );

  const reportOrderOutcome = useCallback(
    (userId: string, orderId: string, outcome: any) =>
      agentService.reportOrderOutcome(userId, orderId, outcome),
    []
  );

  return {
    getRecommendations,
    submitFeedback,
    getQuickReorder,
    assessDeliveryRisk,
    getContextualInfo,
    reportOrderOutcome,
    getPerformanceMetrics: (userId: string) => agentService.getPerformanceMetrics(userId),
    getHealthStatus: () => agentService.getHealthStatus(),
    getUserPatterns: (userId: string) => agentService.getUserPatterns(userId),
    updateUserPreferences: (userId: string, preferences: any) =>
      agentService.updateUserPreferences(userId, preferences),
  };
};