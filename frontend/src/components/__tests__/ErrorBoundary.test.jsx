import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ErrorBoundary from '../ErrorBoundary';

// Component that throws an error
const ThrowError = ({ message }) => {
  throw new Error(message);
};

describe('ErrorBoundary', () => {
  beforeEach(() => {
    // Suppress console.error for expected errors
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    console.error.mockRestore();
  });

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    );
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('renders error UI when there is an error', () => {
    render(
      <ErrorBoundary>
        <ThrowError message="Test error" />
      </ErrorBoundary>
    );
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Test error')).toBeInTheDocument();
  });

  it('shows error details in development mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'development';

    render(
      <ErrorBoundary>
        <ThrowError message="Test error" />
      </ErrorBoundary>
    );

    const detailsButton = screen.getByText('Error details');
    expect(detailsButton).toBeInTheDocument();

    fireEvent.click(detailsButton);
    expect(screen.getByText(/at ThrowError/)).toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });

  it('hides error details in production mode', () => {
    const originalEnv = process.env.NODE_ENV;
    process.env.NODE_ENV = 'production';

    render(
      <ErrorBoundary>
        <ThrowError message="Test error" />
      </ErrorBoundary>
    );

    expect(screen.queryByText('Error details')).not.toBeInTheDocument();

    process.env.NODE_ENV = originalEnv;
  });

  it('resets error state when try again is clicked', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError message="Test error" />
      </ErrorBoundary>
    );

    expect(screen.getByText('Test error')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Try again'));

    rerender(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Test content')).toBeInTheDocument();
  });
});