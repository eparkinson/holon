import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { DashboardView } from '@/views/DashboardView';

describe('DashboardView', () => {
  it('renders dashboard title', () => {
    render(
      <BrowserRouter>
        <DashboardView />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('renders stats cards', () => {
    render(
      <BrowserRouter>
        <DashboardView />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Active Runs')).toBeInTheDocument();
    expect(screen.getByText('Failed Runs (24h)')).toBeInTheDocument();
    expect(screen.getByText('Total Cost')).toBeInTheDocument();
  });
});
