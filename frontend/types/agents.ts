// frontend/types/agents.ts
// Updated interfaces for the simplified 3-agent architecture

export enum AgentType {
    CONTEXT_INTELLIGENCE = 'context_intelligence',
    PREFERENCE_LEARNING = 'preference_learning',
    PREPARATION_TIME = 'preparation_time'
  }

  export enum RiskLevel {
    LOW = 'low',
    MEDIUM = 'medium',
    HIGH = 'high'
  }

  export interface UserContext {
    user_id: string;
    session_id: string;
    current_time: string;
    location?: {
      latitude: number;
      longitude: number;
      address?: string;
    };
    device_info?: {
      user_agent: string;
      screen_size: string;
      platform: string;
    };
    order_history?: Order[];
  }

  export interface AgentResult {
    agent_type: AgentType;
    success: boolean;
    data: Record<string, any>;
    confidence: number;
    execution_time_ms: number;
    metadata?: Record<string, any>;
  }

  // Context Intelligence Agent Types
  export interface ContextIntelligenceData {
    location: {
      deliverable: boolean;
      delivery_zones: DeliveryZone[];
      reason?: string;
    };
    time: {
      meal_period: 'breakfast' | 'lunch' | 'dinner' | 'late_night' | 'overnight';
      urgency: 'low' | 'normal' | 'high';
      current_hour: number;
      is_weekend: boolean;
      suggested_delivery_time: number;
    };
    restaurants: {
      open_count: number;
      busy_restaurants: number[];
      available_restaurants: Restaurant[];
    };
    weather: {
      temperature?: number;
      condition?: string;
      food_preference_hint: 'warm_comfort' | 'light_refreshing' | 'neutral';
      delivery_impact: 'normal' | 'moderate_delay' | 'high_delay';
      available: boolean;
    };
    recommendations: ContextRecommendation[];
  }

  export interface ContextRecommendation {
    type: 'location_warning' | 'time_warning' | 'availability_warning' | 'weather_warning';
    message: string;
    action?: string;
    estimated_delay?: number;
  }

  // Preference Learning Agent Types
  export interface PreferenceLearningData {
    behavioral_patterns: {
      patterns: BehavioralPatterns;
      insights: string[];
      data_sufficient: boolean;
    };
    recommendations: PreferenceRecommendation[];
    user_profile: UserProfile;
    learning_metrics: {
      total_orders: number;
      pattern_confidence: number;
      last_order: string | null;
    };
  }

  export interface BehavioralPatterns {
    temporal_patterns: {
      preferred_hours: Record<string, number>;
      preferred_days: Record<string, number>;
      most_active_hour: number | null;
      weekend_vs_weekday: {
        weekend_orders: number;
        weekday_orders: number;
      };
    };
    cuisine_preferences: {
      preferred_cuisines: Record<string, number>;
      preferred_categories: Record<string, number>;
      cuisine_diversity: number;
      top_cuisine: string | null;
      cuisine_distribution: Record<string, number>;
    };
    price_sensitivity: {
      average_order_value: number;
      price_range: {
        min: number;
        max: number;
        std: number;
      };
      price_category: 'budget_conscious' | 'moderate_spender' | 'premium_buyer';
      price_consistency: 'consistent' | 'varied';
      data_available: boolean;
    };
    restaurant_loyalty: {
      favorite_restaurants: Record<string, number>;
      restaurant_diversity: number;
      loyalty_score: number;
      exploration_tendency: 'high' | 'low';
    };
    customization_patterns: {
      common_customizations: Record<string, number>;
      customization_frequency: number;
      customization_style: 'heavy_customizer' | 'light_customizer';
    };
    ordering_behavior: {
      recent_activity: number;
      ordering_frequency: number;
      reorder_tendency: number;
      decision_style: 'decisive' | 'exploratory';
      last_order_days_ago: number | null;
    };
  }

  export interface PreferenceRecommendation {
    type: 'temporal_match' | 'cuisine_preference' | 'price_match' | 'reorder_suggestion';
    message: string;
    weight: number;
    cuisine?: string;
    price_range?: string;
    action?: string;
  }

  // Problem Prevention Agent Types
  export interface ProblemPreventionData {
    risk_analysis: {
      time_risk: RiskAssessment;
      capacity_risk: RiskAssessment;
      weather_risk: RiskAssessment;
      historical_risk: RiskAssessment;
      location_risk: RiskAssessment;
    };
    validation_results: {
      menu_availability: ValidationResult;
      delivery_area: ValidationResult;
      payment: ValidationResult;
      restaurant_hours: ValidationResult;
    };
    prevention_strategies: PreventionStrategy[];
    overall_risk: {
      score: number;
      level: RiskLevel;
      contributing_factors: string[];
    };
    recommendations: ProblemPreventionRecommendation[];
  }

  export interface RiskAssessment {
    risk_level: RiskLevel;
    estimated_delivery_time?: number;
    late_probability?: number;
    capacity_utilization?: number;
    estimated_delay?: number;
    reason: string;
    recommendation?: string;
  }

  export interface ValidationResult {
    validation_passed: boolean;
    reason?: string;
    note?: string;
    unavailable_items?: Array<{
      item_id: number;
      reason: string;
    }>;
    alternative_suggestion?: string;
  }

  export interface PreventionStrategy {
    type: 'time_adjustment' | 'restaurant_alternative' | 'menu_substitution';
    recommendation: string;
    reason: string;
    alternatives?: any[];
    unavailable_items?: any[];
    alternative_times?: string[];
  }

  export interface ProblemPreventionRecommendation {
    priority: 'low' | 'medium' | 'high';
    type: string;
    message: string;
    action: string;
  }

  // Orchestrator Types
  export interface RecommendationRequest {
    user_context: UserContext;
    request_type: 'full_recommendation' | 'quick_recommendation' | 'risk_assessment' | 'context_only';
    order_details?: Partial<Order>;
    current_menu?: MenuItem[];
  }

  export interface RecommendationResponse {
    success: boolean;
    recommendation_type: string;
    agent_results?: {
      context: {
        success: boolean;
        data: ContextIntelligenceData;
        confidence: number;
        execution_time_ms: number;
      };
      preferences: {
        success: boolean;
        data: PreferenceLearningData;
        confidence: number;
        execution_time_ms: number;
      };
      prevention: {
        success: boolean;
        data: ProblemPreventionData;
        confidence: number;
        execution_time_ms: number;
      };
    };
    combined_recommendations?: CombinedRecommendations;
    orchestrator_metadata: {
      session_id: string;
      request_type: string;
      execution_time_ms: number;
      agents_called: string[];
      total_requests: number;
      error_occurred?: boolean;
    };
    error?: string;
  }

  export interface CombinedRecommendations {
    primary_recommendations: any[];
    contextual_warnings: ContextRecommendation[];
    personalization_insights: string[];
    risk_factors: ProblemPreventionRecommendation[];
    overall_confidence: number;
    unified_recommendations: UnifiedRecommendation[];
  }

  export interface UnifiedRecommendation {
    type: 'warning' | 'time_suggestion' | 'reorder_suggestion' | 'cuisine_suggestion';
    priority: 'low' | 'medium' | 'high';
    title: string;
    message: string;
    action: string;
    source: 'context_intelligence' | 'preference_learning' | 'problem_prevention';
  }

  // Supporting Types
  export interface DeliveryZone {
    id: number;
    name: string;
    area: string;
    estimated_time: number;
  }

  export interface Restaurant {
    id: number;
    name: string;
    cuisine_type: string;
    rating: number;
    estimated_delivery_time: number;
    is_available: boolean;
  }

  export interface MenuItem {
    id: number;
    name: string;
    category: string;
    price: number;
    cuisine_type: string;
    is_available: boolean;
    description: string;
  }

  export interface Order {
    id: number;
    user_id: string;
    restaurant_id: number;
    status: string;
    created_at: string;
    delivered_at?: string;
    estimated_delivery_time?: string;
    total_amount: number;
    items: OrderItem[];
  }

  export interface OrderItem {
    id: number;
    menu_item_id: number;
    quantity: number;
    customizations?: Record<string, any>;
    price: number;
  }

  export interface UserProfile {
    preferences?: Record<string, any>;
    dietary_restrictions?: string[];
    favorite_cuisines?: string[];
    new_user?: boolean;
  }

  // API Service Types
  export interface AgentFeedback {
    agent_type: AgentType;
    feedback: {
      type: string;
      item_id?: number;
      rating?: number;
      accepted?: boolean;
      actual_delivery_time?: number;
      predicted_delivery_time?: number;
      context_factors?: Record<string, any>;
      actual_problems?: string[];
      prevention_effectiveness?: number;
    };
  }

  export interface PerformanceMetrics {
    total_execution_time: number;
    successful_requests: number;
    failed_requests: number;
    agent_performance: Record<string, {
      calls: number;
      avg_time: number;
    }>;
    session_info: {
      session_id: string;
      created_at: string;
      total_requests: number;
      avg_execution_time: number;
    };
  }

  export interface HealthStatus {
    overall_status: 'healthy' | 'degraded' | 'partial';
    orchestrator: {
      status: string;
      session_id: string;
      uptime_seconds: number;
    };
    agents: Record<string, {
      status: 'healthy' | 'inactive' | 'error';
      agent_id?: string;
      created_at?: string;
      is_active?: boolean;
      error?: string;
    }>;
  }