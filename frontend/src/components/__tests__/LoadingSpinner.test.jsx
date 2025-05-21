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
    expect(screen.getByRole('status').querySelector('div')).toHaveClass('w-4 h-4');

    rerender(<LoadingSpinner size="medium" />);
    expect(screen.getByRole('status').querySelector('div')).toHaveClass('w-8 h-8');

    rerender(<LoadingSpinner size="large" />);
    expect(screen.getByRole('status').querySelector('div')).toHaveClass('w-12 h-12');
  });

  it('has correct accessibility attributes', () => {
    render(<LoadingSpinner />);
    const spinner = screen.getByRole('status');
