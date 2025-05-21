import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import OrderForm from '../OrderForm';
import * as apiService from '../services/api';

// Mock the API service
jest.mock('../services/api', () => ({
  startOrder: jest.fn(),
  getMenuData: jest.fn(),
  getHealthRecommendations: jest.fn(),
  getWeatherRecommendations: jest.fn(),
  getDishName: jest.fn(),
  addOrderItem: jest.fn(),
  completeOrder: jest.fn(),
  submitRecommendationFeedback: jest.fn(),
  getCustomerPreviousOrders: jest.fn()
}));

describe('OrderFlow', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();

    // Mock successful API responses
    apiService.startOrder.mockResolvedValue({ success: true, order_data: { id: '123' } });
    apiService.getMenuData.mockResolvedValue({ success: true, menu_data: {} });
    apiService.getHealthRecommendations.mockResolvedValue({
      success: true,
      recommendations: {
        proteins: ['Chicken'],
        sauces: ['Curry Special'],
        base_types: ['Bowl'],
        veggies: ['Bell Pepper'],
        reasoning: 'Test reasoning'
      }
    });
    apiService.getWeatherRecommendations.mockResolvedValue({
      success: true,
      recommendations: {
        base_types: ['Bowl'],
        suggested_base: 'Bowl',
        reasoning: 'Test reasoning'
      }
    });
    apiService.getDishName.mockResolvedValue({
      success: true,
      suggestions: {
        name: 'Healthy Bowl',
        alternatives: ['Fit Bowl', 'Wellness Bowl'],
        format_used: 'Standard format'
      }
    });
    apiService.addOrderItem.mockResolvedValue({ success: true });
    apiService.completeOrder.mockResolvedValue({ success: true });
    apiService.submitRecommendationFeedback.mockResolvedValue({ success: true });
    apiService.getCustomerPreviousOrders.mockResolvedValue({ success: true, orders: [] });
  });

  it('completes the full order flow with all selections', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    const startButton = screen.getByText('Start Order');
    fireEvent.click(startButton);

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    const activityButton = screen.getByText('Active/Gym');
    fireEvent.click(activityButton);
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });
    // Debug: log all button names
    const buttons = screen.getAllByRole('button');
    // eslint-disable-next-line no-console
    console.log('Base selection buttons:', buttons.map(btn => btn.textContent));
    // Select a base type and option (e.g., 'Bowl')
    fireEvent.click(screen.getAllByRole('button', { name: 'Bowl' })[0]);
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Dish name
    await waitFor(() => {
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });
    // Accept the suggested dish name
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Sauce selection (multiple)
    const currySauce = screen.getByText('Curry Special');
    const mintSauce = screen.getByText('Mint Sauce');
    fireEvent.click(currySauce);
    fireEvent.click(mintSauce);
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Veggie selection (multiple)
    const bellPepper = screen.getByText('Bell Pepper');
    const tomato = screen.getByText('Tomato');
    const spinach = screen.getByText('Spinach');
    fireEvent.click(bellPepper);
    fireEvent.click(tomato);
    fireEvent.click(spinach);
    fireEvent.click(screen.getByText('Add to Order'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Review order
    await waitFor(() => {
      expect(screen.getByText('Order Summary')).toBeInTheDocument();
      // Verify dish name is set correctly
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });

    // Complete order
    const completeButton = screen.getByText('Complete Order');
    fireEvent.click(completeButton);

    // Verify order completion
    await waitFor(() => {
      expect(screen.getByText('Order Complete!')).toBeInTheDocument();
    });
  });

  it('handles going back and modifying selections', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });

    // Initial protein selection
    fireEvent.click(screen.getByTestId('protein-chicken'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Base selection
    fireEvent.click(screen.getByText('Bowl'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Dish name
    await waitFor(() => {
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Sauce selection
    fireEvent.click(screen.getByText('Curry Special'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Go back to protein selection
    fireEvent.click(screen.getByText('Back'));
    fireEvent.click(screen.getByText('Back'));
    fireEvent.click(screen.getByText('Back'));
    fireEvent.click(screen.getByText('Back'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Modify protein selection
    fireEvent.click(screen.getByTestId('protein-paneer-indian-cheese'));
    expect(screen.getByTestId('protein-paneer-indian-cheese')).toHaveClass('bg-blue-600');
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Verify base selection is still there
    expect(screen.getByText('Bowl')).toBeInTheDocument();
  });

  it('handles clearing selections', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Select and clear protein
    fireEvent.click(screen.getByTestId('protein-chicken'));
    fireEvent.click(screen.getByText('Clear Selection'));
    expect(screen.getByTestId('protein-chicken')).not.toHaveClass('bg-blue-600');

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Select and clear base
    fireEvent.click(screen.getByText('Bowl'));
    fireEvent.click(screen.getByText('Clear Selection'));
    expect(screen.getByText('Bowl')).not.toHaveClass('bg-blue-600');

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Select and clear sauce
    fireEvent.click(screen.getByText('Curry Special'));
    fireEvent.click(screen.getByText('Clear Selection'));
    expect(screen.getByText('Curry Special')).not.toHaveClass('bg-blue-600');

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Select and clear veggies
    fireEvent.click(screen.getByText('Bell Pepper'));
    fireEvent.click(screen.getByText('Clear Selections'));
    expect(screen.getByText('Bell Pepper')).not.toHaveClass('bg-blue-600');
  });

  it('handles API errors gracefully', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Verify error message
    await waitFor(() => {
      expect(screen.getByText('Failed to get health recommendations.')).toBeInTheDocument();
    });
  });

  it('handles custom dish name input', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });

    // Protein selection
    fireEvent.click(screen.getByTestId('protein-chicken'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Base selection
    fireEvent.click(screen.getByText('Bowl'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Dish name
    await waitFor(() => {
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });

    // Enter custom dish name
    const customNameInput = screen.getByLabelText(/custom dish name/i);
    fireEvent.change(customNameInput, { target: { value: 'My Special Bowl' } });
    fireEvent.click(screen.getByText('Use Custom Name'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Verify custom name in review
    await waitFor(() => {
      expect(screen.getByText('My Special Bowl')).toBeInTheDocument();
    });
  });

  it('handles protein recommendation feedback', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });

    // Verify recommendation is shown
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Verify API call
    await waitFor(() => {
      expect(apiService.submitRecommendationFeedback).toHaveBeenCalledWith(
        'health',
        'accept',
        null,
        '1234567890'
      );
    });
  });

  it('handles base recommendation feedback', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });

    // Protein selection
    fireEvent.click(screen.getByTestId('protein-chicken'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Verify base recommendation is shown
    await waitFor(() => {
      expect(screen.getByText('Bowl')).toBeInTheDocument();
    });

    // Accept recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Verify API call
    await waitFor(() => {
      expect(apiService.submitRecommendationFeedback).toHaveBeenCalledWith(
        'weather',
        'accept',
        null,
        '1234567890'
      );
    });
  });

  it('handles dish name recommendation feedback', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });

    // Protein selection
    fireEvent.click(screen.getByTestId('protein-chicken'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Base selection
    fireEvent.click(screen.getByText('Bowl'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Verify dish name recommendation is shown
    await waitFor(() => {
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });

    // Accept recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Verify API call
    await waitFor(() => {
      expect(apiService.submitRecommendationFeedback).toHaveBeenCalledWith(
        'dish_name',
        'accept',
        null,
        '1234567890'
      );
    });
  });

  it('handles ignoring recommendations', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });

    // Ignore protein recommendation
    fireEvent.click(screen.getByText('Ignore'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Verify API call
    await waitFor(() => {
      expect(apiService.submitRecommendationFeedback).toHaveBeenCalledWith(
        'health',
        'ignore',
        null,
        '1234567890'
      );
    });
  });

  it('handles custom recommendations', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });

    // Enter custom protein
    const customProteinInput = screen.getByLabelText(/custom protein/i);
    fireEvent.change(customProteinInput, { target: { value: 'Tofu' } });
    fireEvent.click(screen.getByText('Use Custom'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Verify API call
    await waitFor(() => {
      expect(apiService.submitRecommendationFeedback).toHaveBeenCalledWith(
        'health',
        'custom',
        'Tofu',
        '1234567890'
      );
    });
  });

  it('calculates correct price for basic order', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });

    // Protein selection (Chicken - $4.50)
    fireEvent.click(screen.getByTestId('protein-chicken'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Base selection (Bowl - $2.00)
    fireEvent.click(screen.getAllByRole('button', { name: 'Bowl' })[0]);
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Dish name
    await waitFor(() => {
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Sauce selection (Curry Special - $1.50)
    fireEvent.click(screen.getByText('Curry Special'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Veggie selection (first 5 free)
    fireEvent.click(screen.getByText('Bell Pepper'));
    fireEvent.click(screen.getByText('Tomato'));
    fireEvent.click(screen.getByText('Spinach'));
    fireEvent.click(screen.getByText('Add to Order'));

    // Verify total price in order summary
    await waitFor(() => {
      expect(screen.getByText('$8.00')).toBeInTheDocument(); // $4.50 + $2.00 + $1.50
    });
  });

  it('calculates correct price with premium items', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });

    // Protein selection (Paneer - $4.00)
    fireEvent.click(screen.getByTestId('protein-paneer-indian-cheese'));
    expect(screen.getByTestId('protein-paneer-indian-cheese')).toHaveClass('bg-blue-600');
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Base selection (Sourdough - $2.50)
    fireEvent.click(screen.getByText('Sourdough'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Dish name
    await waitFor(() => {
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Sauce selection (Curry Special - $1.50)
    fireEvent.click(screen.getByText('Curry Special'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Veggie selection with premium items
    fireEvent.click(screen.getByText('Avocado')); // Premium - $3.00
    fireEvent.click(screen.getByText('Bell Pepper')); // Free
    fireEvent.click(screen.getByText('Tomato')); // Free
    fireEvent.click(screen.getByText('Spinach')); // Free
    fireEvent.click(screen.getByText('Add to Order'));

    // Verify total price in order summary
    await waitFor(() => {
      expect(screen.getByText('$11.00')).toBeInTheDocument(); // $4.00 + $2.50 + $1.50 + $3.00
    });
  });

  it('displays correct order summary details', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for base selection step
    await waitFor(() => {
      expect(screen.getByText('Select Your Base')).toBeInTheDocument();
    });

    // Protein selection
    fireEvent.click(screen.getByTestId('protein-chicken'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Base selection
    fireEvent.click(screen.getAllByRole('button', { name: 'Bowl' })[0]);
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Dish name
    await waitFor(() => {
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Sauce selection
    fireEvent.click(screen.getByText('Curry Special'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Veggie selection
    fireEvent.click(screen.getByText('Bell Pepper'));
    fireEvent.click(screen.getByText('Add to Order'));

    // Verify order summary details
    await waitFor(() => {
      expect(screen.getByText('Order Summary')).toBeInTheDocument();
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
      expect(screen.getByText('Chicken')).toBeInTheDocument();
      expect(screen.getByText('Bowl')).toBeInTheDocument();
      expect(screen.getByText('Curry Special')).toBeInTheDocument();
      expect(screen.getByText('Bell Pepper')).toBeInTheDocument();
      expect(screen.getByText('Customer: John Doe')).toBeInTheDocument();
      expect(screen.getByText('Phone: 1234567890')).toBeInTheDocument();
    });
  });

  it('allows adding multiple items to order', async () => {
    render(<OrderForm />);

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getByText('Start Order')).not.toBeDisabled();
    });

    // Start order
    fireEvent.click(screen.getByText('Start Order'));

    // Customer identification
    const nameInput = screen.getByLabelText(/name/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    fireEvent.change(nameInput, { target: { value: 'John Doe' } });
    fireEvent.change(phoneInput, { target: { value: '1234567890' } });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Activity selection
    fireEvent.click(screen.getByText('Active/Gym'));
    await waitFor(() => {
      expect(screen.getByText('Continue')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByText('Continue'));

    // Wait for protein options to appear
    await waitFor(() => {
      expect(screen.getByTestId('protein-chicken')).toBeInTheDocument();
    });

    // Accept the protein recommendation
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByTestId('protein-chicken')).toHaveClass('bg-blue-600');
    // Wait for loading spinner to disappear
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));
    fireEvent.click(screen.getByText('Bowl'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));
    await waitFor(() => {
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Curry Special'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));
    fireEvent.click(screen.getByText('Bell Pepper'));
    fireEvent.click(screen.getByText('Add to Order'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Add another item
    fireEvent.click(screen.getByText('Add Another Item'));

    // Wait for the activity selection step to appear
    await waitFor(() => {
      expect(screen.getByText('Active/Gym')).toBeInTheDocument();
    });

    // Second item
    fireEvent.click(screen.getByTestId('protein-paneer-indian-cheese'));
    expect(screen.getByTestId('protein-paneer-indian-cheese')).toHaveClass('bg-blue-600');
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));
    fireEvent.click(screen.getByText('Sourdough'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));
    await waitFor(() => {
      expect(screen.getByText('Healthy Bowl')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Accept'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));
    fireEvent.click(screen.getByText('Mint Sauce'));
    expect(screen.getByText('Continue')).not.toBeDisabled();
    fireEvent.click(screen.getByText('Continue'));
    fireEvent.click(screen.getByText('Tomato'));
    fireEvent.click(screen.getByText('Add to Order'));

    // Verify both items in order summary
    await waitFor(() => {
      expect(screen.getByText('Order Summary')).toBeInTheDocument();
      expect(screen.getAllByText(/Healthy Bowl/)).toHaveLength(2);
      expect(screen.getByText('Chicken')).toBeInTheDocument();
      expect(screen.getByText('Paneer/Indian Cheese')).toBeInTheDocument();
    });
  });
});