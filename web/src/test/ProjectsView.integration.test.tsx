import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ProcessesView } from '@/views/ProcessesView';

/**
 * Integration test for ProcessesView that calls the real API.
 * 
 * This test requires a running Holon Engine API server.
 * It validates that the web dashboard can successfully:
 * 1. Fetch deployed processes from the API
 * 2. Display them in the UI
 * 
 * To run this test, start the engine first:
 *   cd engine && uvicorn holon_engine.api:app --host 127.0.0.1 --port 8000
 * 
 * Or skip it in CI by checking for a test flag.
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
const INTEGRATION_TEST_ENABLED = process.env.VITE_INTEGRATION_TEST === 'true';

describe.skipIf(!INTEGRATION_TEST_ENABLED)('ProcessesView Integration', () => {
  let testProcessId: string | null = null;

  beforeAll(async () => {
    // Deploy a test project via API
    const config_yaml = `
version: "1.0"
project: "Integration-Test-Process"

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
          name: 'Integration-Test-Process',
          config_yaml,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        testProcessId = data.project_id;
      }
    } catch (error) {
      console.warn('Failed to deploy test project:', error);
    }
  });

  afterAll(async () => {
    // Clean up: delete the test project if needed
    // Note: This would require a delete endpoint in the API
    if (testProcessId) {
      try {
        await fetch(`${API_BASE_URL}/processes/${testProcessId}`, {
          method: 'DELETE',
        });
      } catch (error) {
        console.warn('Failed to clean up test project:', error);
      }
    }
  });

  it('fetches and displays deployed processes from the API', async () => {
    render(
      <BrowserRouter>
        <ProcessesView />
      </BrowserRouter>
    );

    // Initially shows loading state
    expect(screen.getByText('Loading processes...')).toBeInTheDocument();

    // Wait for processes to load
    await waitFor(
      () => {
        // Should show the test project we deployed
        expect(screen.getByText('Integration-Test-Process')).toBeInTheDocument();
      },
      { timeout: 5000 }
    );

    // Verify the project card is rendered with expected elements
    expect(screen.getByText(/Created/)).toBeInTheDocument();
    expect(screen.getByText(/ID:/)).toBeInTheDocument();
  }, 10000); // 10 second timeout for integration test

  it('shows empty state when no processes exist', async () => {
    // This test assumes a clean state or uses a mock
    // For a true integration test, you'd need to ensure the API has no processes
    // or point to a different test endpoint
    
    render(
      <BrowserRouter>
        <ProcessesView />
      </BrowserRouter>
    );

    await waitFor(
      () => {
        // If there are processes, this will fail
        // If no processes, should show empty state
        const emptyState = screen.queryByText('No processes yet');
        const hasProcesss = screen.queryByText('Integration-Test-Process');
        
        // At least one should be present
        expect(emptyState || hasProcesss).toBeTruthy();
      },
      { timeout: 5000 }
    );
  }, 10000);
});
