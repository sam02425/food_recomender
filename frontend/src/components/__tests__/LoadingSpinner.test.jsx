import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import LoadingSpinner from '../LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders with default props', () => {
    render(<LoadingSpinner />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders with custom text', () => {
    render(<LoadingSpinner text="Please wait..." />);
    expect(screen.getByText('Please wait...')).toBeInTheDocument();
  });

  it('renders without text', () => {
    render(<LoadingSpinner text="" />);
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  it('applies correct size classes', () => {
    const { rerender } = render(<LoadingSpinner size="small" />);
    const spinnerDiv = screen.getByRole('status').querySelector('div');
    expect(spinnerDiv).toHaveClass('w-4 h-4', 'animate-spin');

    rerender(<LoadingSpinner size="medium" />);
    expect(spinnerDiv).toHaveClass('w-8 h-8', 'animate-spin');

    rerender(<LoadingSpinner size="large" />);
    expect(spinnerDiv).toHaveClass('w-12 h-12', 'animate-spin');
  });

  it('has correct accessibility attributes', () => {
    render(<LoadingSpinner />);
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveAttribute('aria-live', 'polite');
  });

  it('renders with correct SVG structure', () => {
    render(<LoadingSpinner />);
    const svg = screen.getByRole('status').querySelector('svg');
    expect(svg).toHaveClass('text-blue-600');
    expect(svg.querySelector('circle')).toHaveClass('opacity-25');
    expect(svg.querySelector('path')).toHaveClass('opacity-75');
  });

  it('applies correct container classes', () => {
    render(<LoadingSpinner />);
    const container = screen.getByRole('status');
    expect(container).toHaveClass('flex', 'flex-col', 'items-center', 'justify-center', 'p-4');
  });
});
