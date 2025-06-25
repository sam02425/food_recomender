import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Start a new order
 */
export const startOrder = async () => {
  try {
    const response = await apiClient.post('/start-order');
    return response.data;
  } catch (error) {
    console.error('Error starting order:', error);
    throw error;
  }
};

/**
 * Get health recommendations based on activity level and customer data
 */
export const getHealthRecommendations = async (activityLevel, customerPhone = null) => {
  try {
    const response = await apiClient.post('/health-recommendations', {
      activity_level: activityLevel,
      customer_phone: customerPhone, // Include customer phone for personalization
    });
    return response.data;
  } catch (error) {
    console.error('Error getting health recommendations:', error);
    throw error;
  }
};

/**
 * Get weather-based recommendations
 */
export const getWeatherRecommendations = async (customerPhone = null) => {
  try {
    const response = await apiClient.post('/weather-recommendations', {
      customer_phone: customerPhone, // Include customer phone for personalization
    });
    return response.data;
  } catch (error) {
    console.error('Error getting weather recommendations:', error);
    throw error;
  }
};

/**
 * Get dish name suggestions
 */
export const getDishName = async (selections) => {
  try {
    const response = await apiClient.post('/dish-name', { selections });
    return response.data;
  } catch (error) {
    console.error('Error getting dish name suggestions:', error);
    throw error;
  }
};

/**
 * Submit feedback on recommendations
 */
export const submitRecommendationFeedback = async (recommendationType, feedback, customSuggestion = null, customerPhone = null) => {
  try {
    const response = await apiClient.post('/recommendation-feedback', {
      recommendation_type: recommendationType,
      feedback,
      custom_suggestion: customSuggestion,
      customer_phone: customerPhone, // Include customer phone
    });
    return response.data;
  } catch (error) {
    console.error('Error submitting recommendation feedback:', error);
    throw error;
  }
};

/**
 * Add an item to the current order
 */
export const addOrderItem = async (selections) => {
  try {
    const response = await apiClient.post('/add-item', { selections });
    return response.data;
  } catch (error) {
    console.error('Error adding order item:', error);
    throw error;
  }
};

/**
 * Complete the current order
 */
export const completeOrder = async (customerPhone = null, customerName = null) => {
  try {
    const response = await apiClient.post('/complete-order', {
      customer_phone: customerPhone,
      customer_name: customerName
    });
    return response.data;
  } catch (error) {
    console.error('Error completing order:', error);
    throw error;
  }
};

/**
 * Get menu data
 */
export const getMenuData = async () => {
  try {
    const response = await apiClient.get('/menu-data');
    return response.data;
  } catch (error) {
    console.error('Error getting menu data:', error);
    throw error;
  }
};

/**
 * Get customer's previous orders based on phone number
 */
export const getCustomerPreviousOrders = async (phoneNumber) => {
  try {
    const response = await apiClient.get('/customer-orders', {
      params: { phone: phoneNumber }
    });
    return response.data;
  } catch (error) {
    console.error('Error getting customer previous orders:', error);
    throw error;
  }
};

/**
 * Update customer information
 */
export const updateCustomerInfo = async (customerData) => {
  try {
    const response = await apiClient.post('/update-customer', customerData);
    return response.data;
  } catch (error) {
    console.error('Error updating customer info:', error);
    throw error;
  }
};

// ==== ML-POWERED RECOMMENDATION FUNCTIONS ====

/**
 * Get ML-powered comprehensive recommendations
 */
export const getMLRecommendations = async (userId, context, options = {}) => {
  try {
    const payload = {
      user_id: userId,
      context: {
        activity_level: context.activityLevel || 'work',
        mood: context.mood || 'neutral',
        weather: {
          condition: context.weatherCondition || 'sunny'
        },
        time_of_day: context.timeOfDay || 'afternoon',
        customer_history: context.customerHistory || []
      },
      n_recommendations: options.nRecommendations || 5,
      include_explanations: options.includeExplanations !== false
    };

    const response = await apiClient.post('/ml/recommendations', payload);
    return response.data;
  } catch (error) {
    console.error('Error getting ML recommendations:', error);
    throw error;
  }
};

/**
 * Get hybrid recommendations (ML + Traditional)
 */
export const getHybridRecommendations = async (userId, context, options = {}) => {
  try {
    const params = new URLSearchParams({
      activity_level: context.activityLevel || 'work',
      mood: context.mood || 'neutral',
      weather_condition: context.weatherCondition || 'sunny',
      time_of_day: context.timeOfDay || 'afternoon',
      n_recommendations: options.nRecommendations || 5
    });

    const response = await apiClient.get(`/ml/recommendations/hybrid/${userId}?${params}`);
    return response.data;
  } catch (error) {
    console.error('Error getting hybrid recommendations:', error);
    throw error;
  }
};

/**
 * Submit feedback to ML models
 */
export const submitMLFeedback = async (userId, feedbackData, context = {}) => {
  try {
    const payload = {
      user_id: userId,
      feedback_type: feedbackData.type || 'explicit', // 'explicit', 'implicit', 'text'
      feedback_data: {
        explicit_ratings: feedbackData.explicitRatings || {},
        selections: feedbackData.selections || {},
        text_feedback: feedbackData.textFeedback || '',
        order_details: feedbackData.orderDetails || {},
        feedback_type: feedbackData.type || 'explicit'
      },
      context: context
    };

    const response = await apiClient.post('/ml/feedback', payload);
    return response.data;
  } catch (error) {
    console.error('Error submitting ML feedback:', error);
    throw error;
  }
};

/**
 * Get user's learned preferences from ML models
 */
export const getUserMLPreferences = async (userId) => {
  try {
    const response = await apiClient.get(`/ml/user/preferences/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting user ML preferences:', error);
    throw error;
  }
};

/**
 * Analyze text feedback using NLP
 */
export const analyzeTextFeedback = async (feedbackText, orderDetails = {}) => {
  try {
    const response = await apiClient.post('/ml/analyze/feedback', null, {
      params: {
        feedback_text: feedbackText
      },
      data: orderDetails
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing text feedback:', error);
    throw error;
  }
};

/**
 * Get ML model insights and performance metrics
 */
export const getMLModelInsights = async () => {
  try {
    const response = await apiClient.get('/ml/models/insights');
    return response.data;
  } catch (error) {
    console.error('Error getting ML model insights:', error);
    throw error;
  }
};

/**
 * Trigger retraining of ML models
 */
export const retrainMLModels = async () => {
  try {
    const response = await apiClient.post('/ml/models/retrain');
    return response.data;
  } catch (error) {
    console.error('Error triggering ML model retraining:', error);
    throw error;
  }
};

/**
 * Smart recommendation function that chooses the best approach
 * Falls back gracefully from ML to traditional recommendations
 */
export const getSmartRecommendations = async (userId, context, options = {}) => {
  try {
    // First try ML-powered recommendations
    if (options.preferML !== false) {
      try {
        const mlResults = await getMLRecommendations(userId, context, {
          ...options,
          includeExplanations: true
        });

        if (mlResults.success && mlResults.confidence > 0.6) {
          return {
            ...mlResults,
            source: 'ml_primary',
            fallback_available: true
          };
        }
      } catch (mlError) {
        console.warn('ML recommendations failed, falling back to traditional:', mlError);
      }
    }

    // Fallback to traditional recommendations
    const [healthRecs, weatherRecs] = await Promise.all([
      getHealthRecommendations(context.activityLevel, userId),
      getWeatherRecommendations(userId)
    ]);

    // Convert traditional format to unified format
    const traditionalRecommendations = [
      ...(healthRecs.proteins || []).map(item => ({
        category: 'protein',
        item: item,
        predicted_rating: 4.0,
        confidence: 0.8,
        source: 'health_agent',
        reason: healthRecs.reasoning || 'Health-based recommendation'
      })),
      ...(healthRecs.sauces || []).map(item => ({
        category: 'sauce',
        item: item,
        predicted_rating: 4.0,
        confidence: 0.8,
        source: 'health_agent',
        reason: healthRecs.reasoning || 'Health-based recommendation'
      })),
      ...(weatherRecs.base_types || []).map(item => ({
        category: 'base',
        item: item,
        predicted_rating: 4.0,
        confidence: 0.7,
        source: 'weather_agent',
        reason: weatherRecs.reasoning || 'Weather-based recommendation'
      }))
    ].slice(0, options.nRecommendations || 5);

    return {
      success: true,
      recommendations: traditionalRecommendations,
      explanations: {
        overview: `Recommendations based on your ${context.activityLevel} activity and current weather conditions.`
      },
      confidence: 0.8,
      source: 'traditional_fallback',
      traditional_details: {
        health_recommendations: healthRecs,
        weather_recommendations: weatherRecs
      }
    };

  } catch (error) {
    console.error('Error getting smart recommendations:', error);
    throw error;
  }
};

// ========================
// DIETARY RESTRICTIONS API
// ========================

/**
 * Get all available dietary restrictions
 */
export const getAvailableDietaryRestrictions = async () => {
  try {
    const response = await apiClient.get('/dietary/restrictions/available');
    return response.data;
  } catch (error) {
    console.error('Error getting available dietary restrictions:', error);
    throw error;
  }
};

/**
 * Get all available allergen categories
 */
export const getAvailableAllergens = async () => {
  try {
    const response = await apiClient.get('/dietary/allergens/available');
    return response.data;
  } catch (error) {
    console.error('Error getting available allergens:', error);
    throw error;
  }
};

/**
 * Set dietary restrictions for a user
 */
export const setUserDietaryRestrictions = async (userId, restrictions) => {
  try {
    const response = await apiClient.post('/dietary/restrictions/set', {
      user_id: userId,
      restrictions: restrictions
    });
    return response.data;
  } catch (error) {
    console.error('Error setting dietary restrictions:', error);
    throw error;
  }
};

/**
 * Set allergens for a user
 */
export const setUserAllergens = async (userId, allergens) => {
  try {
    const response = await apiClient.post('/dietary/allergens/set', {
      user_id: userId,
      allergens: allergens
    });
    return response.data;
  } catch (error) {
    console.error('Error setting allergens:', error);
    throw error;
  }
};

/**
 * Get user's complete dietary profile
 */
export const getUserDietaryProfile = async (userId) => {
  try {
    const response = await apiClient.get(`/dietary/profile/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting user dietary profile:', error);
    throw error;
  }
};

/**
 * Get safe food options for a user based on their restrictions
 */
export const getSafeOptions = async (userId, category) => {
  try {
    const response = await apiClient.post('/dietary/options/safe', {
      user_id: userId,
      category: category
    });
    return response.data;
  } catch (error) {
    console.error('Error getting safe options:', error);
    throw error;
  }
};

/**
 * Filter recommendations based on dietary restrictions
 */
export const filterRecommendations = async (userId, recommendations) => {
  try {
    const response = await apiClient.post('/dietary/recommendations/filter', {
      user_id: userId,
      recommendations: recommendations
    });
    return response.data;
  } catch (error) {
    console.error('Error filtering recommendations:', error);
    throw error;
  }
};

/**
 * Get detailed ingredient information for a menu item
 */
export const getIngredientInfo = async (itemName) => {
  try {
    const response = await apiClient.get(`/dietary/ingredients/${encodeURIComponent(itemName)}`);
    return response.data;
  } catch (error) {
    console.error('Error getting ingredient info:', error);
    throw error;
  }
};

/**
 * Clear all dietary restrictions for a user
 */
export const clearUserDietaryRestrictions = async (userId) => {
  try {
    const response = await apiClient.delete(`/dietary/profile/${userId}/restrictions`);
    return response.data;
  } catch (error) {
    console.error('Error clearing dietary restrictions:', error);
    throw error;
  }
};

/**
 * Clear all allergens for a user
 */
export const clearUserAllergens = async (userId) => {
  try {
    const response = await apiClient.delete(`/dietary/profile/${userId}/allergens`);
    return response.data;
  } catch (error) {
    console.error('Error clearing allergens:', error);
    throw error;
  }
};

/**
 * Get statistics about dietary restrictions usage
 */
export const getDietaryStats = async () => {
  try {
    const response = await apiClient.get('/dietary/stats');
    return response.data;
  } catch (error) {
    console.error('Error getting dietary stats:', error);
    throw error;
  }
};