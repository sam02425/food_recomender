import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import OrderForm from '../OrderForm';
import * as apiService from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  getHealthRecommendations: jest.fn(),
  getWeatherRecommendations: jest.fn(),
  getDishNameSuggestions: jest.fn(),
  addOrderItem: jest.fn(),
  completeOrder: jest.fn()
}));

describe('Order Flow Integration', () => {
  const mockCustomerData = {
    name: 'John Doe',
    phoneNumber: '1234567890'
  };

  const mockRecommendations = {
    proteins: ['Chicken', 'Paneer/Indian Cheese'],
    sauces: ['Curry Special', 'Mint Sauce'],
    base_types: ['Bowl'],
    veggies: ['Bell Pepper', 'Spinach', 'Tomato'],
    reasoning: 'Based on your activity level'
  };

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Setup default mock responses
    apiService.getHealthRecommendations.mockResolvedValue({
      success: true,
      recommendations: mockRecommendations
    });

    apiService.getWeatherRecommendations.mockResolvedValue({
      success: true,
      recommendations: mockRecommendations
    });

    apiService.getDishNameSuggestions.mockResolvedValue({
      success: true,
      suggestions: {
        name: 'Healthy Bowl',
        alternatives: ['Power Bowl', 'Energy Bowl']
      }
    });

    apiService.addOrderItem.mockResolvedValue({
      success: true
    });

    apiService.completeOrder.mockResolvedValue({
      success: true,
      orderId: '12345'
    });
  });

  it('completes the full order flow successfully', async () => {
    render(<OrderForm />);

    // Step 1: Activity Selection
    fireEvent.click(screen.getByText('Active/Gym'));
    fireEvent.click(screen.getByText('Continue'));

    // Step 2: Protein Selection
    await waitFor(() => {
      expect(screen.getByText('Select Your Protein')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Chicken'));
    fireEvent.click(screen.getByText('Continue'));

    // Step 3: Base Selection
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Bowl'));
    fireEvent.click(screen.getByText('Continue'));

    // Step 4: Dish Name
    await waitFor(() => {
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Step 5: Sauce Selection
    await waitFor(() => {
      expect(screen.getByText('Select Your Sauce')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Curry Special'));
    fireEvent.click(screen.getByText('Continue'));

    // Step 6: Veggie Selection
    await waitFor(() => {
      expect(screen.getByText('Select Your Veggies')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Bell Pepper'));
    fireEvent.click(screen.getByText('Spinach'));
    fireEvent.click(screen.getByText('Add to Order'));

    // Step 7: Review and Complete
    await waitFor(() => {
      expect(screen.getByText('Order Summary')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Complete Order'));

    // Verify API calls
    expect(apiService.getHealthRecommendations).toHaveBeenCalled();
    expect(apiService.getWeatherRecommendations).toHaveBeenCalled();
    expect(apiService.getDishNameSuggestions).toHaveBeenCalled();
    expect(apiService.addOrderItem).toHaveBeenCalled();
    expect(apiService.completeOrder).toHaveBeenCalled();
  });

  it('handles API errors gracefully', async () => {
    // Mock API error
    apiService.getHealthRecommendations.mockRejectedValue(new Error('API Error'));

    render(<OrderForm />);

    // Step 1: Activity Selection
    fireEvent.click(screen.getByText('Active/Gym'));
    fireEvent.click(screen.getByText('Continue'));

    // Should show error state
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('allows going back and modifying selections', async () => {
    render(<OrderForm />);

    // Complete initial steps
    fireEvent.click(screen.getByText('Active/Gym'));
    fireEvent.click(screen.getByText('Continue'));

    await waitFor(() => {
      expect(screen.getByText('Select Your Protein')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Chicken'));
    fireEvent.click(screen.getByText('Continue'));

    // Go back
    fireEvent.click(screen.getByText('Back'));

    // Should be back at protein selection
    await waitFor(() => {
      expect(screen.getByText('Select Your Protein')).toBeInTheDocument();
    });

    // Change selection
    fireEvent.click(screen.getByText('Paneer/Indian Cheese'));
    fireEvent.click(screen.getByText('Continue'));

    // Should proceed with new selection
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });
  });
});