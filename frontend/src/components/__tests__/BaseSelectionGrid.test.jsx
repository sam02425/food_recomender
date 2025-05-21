import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import BaseSelectionGrid from '../BaseSelectionGrid';

describe('BaseSelectionGrid', () => {
  const mockBaseTypes = {
    'Biryani': [
      { name: 'Rice', price: 2.00, description: 'Fragrant basmati rice' }
    ],
    'Sandwich & Subs': [
      { name: 'Sourdough', price: 2.50, description: 'Tangy artisan bread' }
    ]
  };

  const defaultProps = {
    title: 'Select Your Base',
    baseTypes: mockBaseTypes,
    recommendations: ['Biryani'],
    selectedBaseType: '',
    selectedBaseOption: '',
    onSelect: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the component with title', () => {
    render(<BaseSelectionGrid {...defaultProps} />);
    expect(screen.getByText('Select Your Base')).toBeInTheDocument();
  });

  it('renders all base types and their options', () => {
    render(<BaseSelectionGrid {...defaultProps} />);
    expect(screen.getByText('Biryani')).toBeInTheDocument();
    expect(screen.getByText('Sandwich & Subs')).toBeInTheDocument();
    expect(screen.getByText('Rice')).toBeInTheDocument();
    expect(screen.getByText('Sourdough')).toBeInTheDocument();
  });

  it('highlights recommended base types', () => {
    render(<BaseSelectionGrid {...defaultProps} />);
    const biryaniHeader = screen.getByText('Biryani').closest('h3');
    expect(biryaniHeader).toHaveClass('text-green-600');
  });

  it('calls onSelect when an option is clicked', () => {
    render(<BaseSelectionGrid {...defaultProps} />);
    fireEvent.click(screen.getByText('Rice'));
    expect(defaultProps.onSelect).toHaveBeenCalledWith('Biryani', 'Rice');
  });

  it('deselects when clicking the same option again', () => {
    const props = {
      ...defaultProps,
      selectedBaseType: 'Biryani',
      selectedBaseOption: 'Rice'
    };
    render(<BaseSelectionGrid {...props} />);
    fireEvent.click(screen.getByText('Rice'));
    expect(defaultProps.onSelect).toHaveBeenCalledWith('', '');
  });

  it('displays prices correctly', () => {
    render(<BaseSelectionGrid {...defaultProps} />);
    expect(screen.getByText('$2.00')).toBeInTheDocument();
    expect(screen.getByText('$2.50')).toBeInTheDocument();
  });

  it('shows descriptions on hover', () => {
    render(<BaseSelectionGrid {...defaultProps} />);
    const riceOption = screen.getByText('Rice').closest('div');
    expect(riceOption).toHaveAttribute('title', 'Fragrant basmati rice');
  });

  it('applies correct styling for selected items', () => {
    const props = {
      ...defaultProps,
      selectedBaseType: 'Biryani',
      selectedBaseOption: 'Rice'
    };
    render(<BaseSelectionGrid {...props} />);
    const selectedOption = screen.getByText('Rice').closest('div');
    expect(selectedOption).toHaveClass('border-blue-500', 'bg-blue-50');
  });
});