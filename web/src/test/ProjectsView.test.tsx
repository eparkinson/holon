import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ProjectsView } from '@/views/ProjectsView';

describe('ProjectsView', () => {
  it('renders projects title', () => {
    render(
      <BrowserRouter>
        <ProjectsView />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Projects')).toBeInTheDocument();
  });

  it('shows projects when available', () => {
    render(
      <BrowserRouter>
        <ProjectsView />
      </BrowserRouter>
    );
    
    // The view has mock data showing a project
    expect(screen.getByText('Daily Market Briefing')).toBeInTheDocument();
  });
});
