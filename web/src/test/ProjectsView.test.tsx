import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ProjectsView } from '@/views/ProjectsView';
import { apiClient } from '@/services/api';

// Mock the API client
vi.mock('@/services/api', () => ({
  apiClient: {
    listProjects: vi.fn(),
    triggerRun: vi.fn(),
  },
}));

describe('ProjectsView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders projects title', () => {
    vi.mocked(apiClient.listProjects).mockResolvedValue([]);
    
    render(
      <BrowserRouter>
        <ProjectsView />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Projects')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    vi.mocked(apiClient.listProjects).mockImplementation(() => new Promise(() => {}));
    
    render(
      <BrowserRouter>
        <ProjectsView />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Loading projects...')).toBeInTheDocument();
  });

  it('shows projects when available', async () => {
    const mockProjects = [
      {
        id: '123e4567-e89b-12d3-a456-426614174000',
        name: 'Daily Market Briefing',
        created_at: '2024-01-01T00:00:00Z',
      },
    ];
    
    vi.mocked(apiClient.listProjects).mockResolvedValue(mockProjects);
    
    render(
      <BrowserRouter>
        <ProjectsView />
      </BrowserRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('Daily Market Briefing')).toBeInTheDocument();
    });
  });

  it('shows empty state when no projects', async () => {
    vi.mocked(apiClient.listProjects).mockResolvedValue([]);
    
    render(
      <BrowserRouter>
        <ProjectsView />
      </BrowserRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText('No projects yet')).toBeInTheDocument();
    });
  });

  it('shows error state when API fails', async () => {
    vi.mocked(apiClient.listProjects).mockRejectedValue(new Error('Network error'));
    
    render(
      <BrowserRouter>
        <ProjectsView />
      </BrowserRouter>
    );
    
    await waitFor(() => {
      expect(screen.getByText(/Error loading projects/)).toBeInTheDocument();
    });
  });
});
