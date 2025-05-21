import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ErrorBoundary from '../ErrorBoundary';

// Component that throws an error
const ThrowError = ({ message }) => {
  throw new Error(message);
};

describe('ErrorBoundary', () => {
  const originalEnv = process.env.NODE_ENV;

  beforeEach(() => {
    // Suppress console.error for expected errors
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    console.error.mockRestore();
    // Reset NODE_ENV after each test
    process.env.NODE_ENV = originalEnv;
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

  it('shows error details in development mode', async () => {
    process.env.NODE_ENV = 'development';

    render(
      <ErrorBoundary>
        <ThrowError message="Test error" />
      </ErrorBoundary>
    );

    const detailsButton = screen.getByText('Error details');
    expect(detailsButton).toBeInTheDocument();

    fireEvent.click(detailsButton);

    // Check for a <pre> element inside details
    const details = screen.getByText('Error details').closest('details');
    const pre = details && details.querySelector('pre');
    expect(pre).toBeTruthy();
  });

  it('hides error details in production mode', () => {
    process.env.NODE_ENV = 'production';

    render(
      <ErrorBoundary>
        <ThrowError message="Test error" />
      </ErrorBoundary>
    );

    expect(screen.queryByText('Error details')).not.toBeInTheDocument();
  });

  it('resets error state when try again is clicked', async () => {
    const { rerender } = render(
      <ErrorBoundary>
        <TestComponent />
      </ErrorBoundary>
    );

    // Trigger error
    rerender(
      <ErrorBoundary>
        <TestComponent shouldThrow={true} />
      </ErrorBoundary>
    );

    // Verify error is shown
    expect(screen.getByText('Test error')).toBeInTheDocument();

    // Click try again and rerender with non-error state
    fireEvent.click(screen.getByText('Try again'));
    rerender(
      <ErrorBoundary>
        <TestComponent shouldThrow={false} />
      </ErrorBoundary>
    );

    // Wait for the error state to be cleared and test content to appear
    await waitFor(() => {
      expect(screen.queryByText('Test error')).not.toBeInTheDocument();
      expect(screen.getByText('Test content')).toBeInTheDocument();
    }, { timeout: 2000 });
  });
});