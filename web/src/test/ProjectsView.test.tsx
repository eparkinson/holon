import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ProcessesView } from '@/views/ProcessesView';
import { apiClient } from '@/services/api';

// Mock the API client
vi.mock('@/services/api', () => ({
  apiClient: {
    listProcesses: vi.fn(),
    triggerRun: vi.fn(),
  },
}));

describe('ProcessesView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders processes title', () => {
    vi.mocked(apiClient.listProcesses).mockResolvedValue([]);
    
    render(
      <BrowserRouter>
        <ProcessesView />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Processes')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    vi.mocked(apiClient.listProcesses).mockImplementation(() => new Promise(() => {}));
    
    render(
      <BrowserRouter>
        <ProcessesView />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Loading processes...')).toBeInTheDocument();
  });

  it('shows processes when available', async () => {
    const mockProcesses = [
      {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Daily Market Briefing',
        created_at: '2024-01-01T00:00:00Z',
      },
    ];
    
    vi.mocked(apiClient.listProcesses).mockResolvedValue(mockProcesses);
    
    render(
      <BrowserRouter>
        <ProcessesView />
      </BrowserRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Daily Market Briefing')).toBeInTheDocument();
    });
  });

  it('shows empty state when no processes', async () => {
    vi.mocked(apiClient.listProcesses).mockResolvedValue([]);
    
    render(
      <BrowserRouter>
        <ProcessesView />
      </BrowserRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('No processes yet')).toBeInTheDocument();
    });
  });

  it('shows error state when API fails', async () => {
    vi.mocked(apiClient.listProcesses).mockRejectedValue(new Error('Network error'));
    
    render(
      <BrowserRouter>
        <ProcessesView />
      </BrowserRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText(/Error loading processes/)).toBeInTheDocument();
    });
  });
});
