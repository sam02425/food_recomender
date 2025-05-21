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
    const riceOption = screen.getByRole('button', { name: /Rice/i });
    expect(riceOption).toBeInTheDocument();
    fireEvent.click(riceOption);
    expect(defaultProps.onSelect).toHaveBeenCalledWith('Biryani', 'Rice');
  });

  it('deselects when clicking the same option again', () => {
    const props = {
      ...defaultProps,
      selectedBaseType: 'Biryani',
      selectedBaseOption: 'Rice'
    };
    render(<BaseSelectionGrid {...props} />);
    const riceOption = screen.getByRole('button', { name: /Rice/i });
    expect(riceOption).toBeInTheDocument();
    fireEvent.click(riceOption);
    expect(defaultProps.onSelect).toHaveBeenCalledWith('', '');
  });

  it('displays prices correctly', () => {
    render(<BaseSelectionGrid {...defaultProps} />);
    expect(screen.getByText('$2.00')).toBeInTheDocument();
    expect(screen.getByText('$2.50')).toBeInTheDocument();
  });

  it('shows descriptions on hover', () => {
    render(<BaseSelectionGrid {...defaultProps} />);
    const riceOption = screen.getByRole('button', { name: /Rice/i });
    expect(riceOption).toHaveAttribute('title', 'Fragrant basmati rice');
  });

  it('applies correct styling for selected items', () => {
    const props = {
      ...defaultProps,
      selectedBaseType: 'Biryani',
      selectedBaseOption: 'Rice'
    };
    render(<BaseSelectionGrid {...props} />);
    // Find all clickable base option divs
    const baseOptionDivs = Array.from(document.querySelectorAll('div.cursor-pointer'));
    let riceOptionDiv = null;
    for (const div of baseOptionDivs) {
      const span = div.querySelector('span.font-medium');
      if (span && span.textContent.trim() === 'Rice') {
        riceOptionDiv = div;
        break;
      }
    }
    expect(riceOptionDiv).toBeTruthy();
    expect(riceOptionDiv).toHaveClass('border-blue-500');
  });
});