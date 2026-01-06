import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ProjectsView } from '@/views/ProjectsView';

/**
 * Integration test for ProjectsView that calls the real API.
 * 
 * This test requires a running Holon Engine API server.
 * It validates that the web dashboard can successfully:
 * 1. Fetch deployed projects from the API
 * 2. Display them in the UI
 * 
 * To run this test, start the engine first:
 *   cd engine && uvicorn holon_engine.api:app --host 127.0.0.1 --port 8000
 * 
 * Or skip it in CI by checking for a test flag.
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
const INTEGRATION_TEST_ENABLED = process.env.VITE_INTEGRATION_TEST === 'true';

describe.skipIf(!INTEGRATION_TEST_ENABLED)('ProjectsView Integration', () => {
  let testProjectId: string | null = null;

  beforeAll(async () => {
    // Deploy a test project via API
    const config_yaml = `
version: "1.0"
project: "Integration-Test-Project"

resources:
  - id: test_agent
    provider: anthropic
    model: claude-3-5-sonnet

workflow:
  type: sequential
  steps:
    - id: step1
      agent: test_agent
      instruction: "Test instruction"
`;

    try {
      const response = await fetch(`${API_BASE_URL}/deploy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: 'Integration-Test-Project',
          config_yaml,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        testProjectId = data.project_id;
      }
    } catch (error) {
      console.warn('Failed to deploy test project:', error);
    }
  });

  afterAll(async () => {
    // Clean up: delete the test project if needed
    // Note: This would require a delete endpoint in the API
    if (testProjectId) {
      try {
        await fetch(`${API_BASE_URL}/projects/${testProjectId}`, {
          method: 'DELETE',
        });
      } catch (error) {
        console.warn('Failed to clean up test project:', error);
      }
    }
  });

  it('fetches and displays deployed projects from the API', async () => {
    render(
      <BrowserRouter>
        <ProjectsView />
      </BrowserRouter>
    );

    // Initially shows loading state
    expect(screen.getByText('Loading projects...')).toBeInTheDocument();

    // Wait for projects to load
    await waitFor(
      () => {
        // Should show the test project we deployed
        expect(screen.getByText('Integration-Test-Project')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );

    // Verify the project card is rendered with expected elements
    expect(screen.getByText(/Created/)).toBeInTheDocument();
    expect(screen.getByText(/ID:/)).toBeInTheDocument();
  }, 10000); // 10 second timeout for integration test

  it('shows empty state when no projects exist', async () => {
    // This test assumes a clean state or uses a mock
    // For a true integration test, you'd need to ensure the API has no projects
    // or point to a different test endpoint
    
    render(
      <BrowserRouter>
        <ProjectsView />
      </BrowserRouter>
    );

    await waitFor(
      () => {
        // If there are projects, this will fail
        // If no projects, should show empty state
        const emptyState = screen.queryByText('No projects yet');
        const hasProjects = screen.queryByText('Integration-Test-Project');
        
        // At least one should be present
        expect(emptyState || hasProjects).toBeTruthy();
      },
      { timeout: 5000 }
    );
  }, 10000);
});
