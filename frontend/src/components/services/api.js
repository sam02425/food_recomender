import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

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