import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { LoadingView, ErrorView, EmptyView } from './StateViews';

describe('StateViews components', () => {
  it('renders LoadingView with custom message', () => {
    render(<LoadingView message="Loading test data..." />);
    expect(screen.getByText('Loading test data...')).toBeDefined();
    expect(screen.getByText('Grounded directly in Elexon BMRS January 2026 data')).toBeDefined();
  });

  it('renders ErrorView and handles retry clicks', () => {
    const handleRetry = vi.fn();
    render(<ErrorView message="Network timeout error" onRetry={handleRetry} />);
    
    expect(screen.getByText('Failed to load data')).toBeDefined();
    expect(screen.getByText('Network timeout error')).toBeDefined();

    const retryButton = screen.getByRole('button', { name: /retry request/i });
    expect(retryButton).toBeDefined();
    fireEvent.click(retryButton);
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });

  it('renders EmptyView and handles reset filters click', () => {
    const handleReset = vi.fn();
    render(
      <EmptyView
        title="Custom empty title"
        description="Custom empty description"
        onReset={handleReset}
      />
    );

    expect(screen.getByText('Custom empty title')).toBeDefined();
    expect(screen.getByText('Custom empty description')).toBeDefined();

    const resetButton = screen.getByRole('button', { name: /reset filters/i });
    expect(resetButton).toBeDefined();
    fireEvent.click(resetButton);
    expect(handleReset).toHaveBeenCalledTimes(1);
  });

  it('renders ErrorView with readable 422 validation error message', () => {
    const error422 = "API Error 422: hourly_only: Input should be a valid boolean, unable to interpret input";
    render(<ErrorView message={error422} />);
    expect(screen.getByText('Failed to load data')).toBeDefined();
    expect(screen.getByText(error422)).toBeDefined();
  });
});
