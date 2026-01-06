# Web Integration Tests

## Running Integration Tests

The integration tests validate that the web dashboard correctly communicates with the Holon Engine API.

### Prerequisites

1. Start the Holon Engine API server:
   ```bash
   cd engine
   uvicorn holon_engine.api:app --host 127.0.0.1 --port 8000
   ```

2. Set the integration test environment variable:
   ```bash
   export VITE_INTEGRATION_TEST=true
   ```

3. Run the tests:
   ```bash
   cd web
   npm test -- --run
   ```

### What the Integration Tests Validate

The `ProjectsView.integration.test.tsx` test validates:

1. **API Communication**: The web dashboard successfully calls the `/api/v1/projects` endpoint
2. **Data Display**: Deployed projects are correctly displayed in the UI
3. **Real-world behavior**: The full stack works together (web → API → persistence)

### CI/CD

By default, integration tests are skipped in CI because they require a running API server. The tests check for the `VITE_INTEGRATION_TEST` environment variable and only run when it's set to `'true'`.

To run integration tests in CI:
1. Start the API server in the background
2. Set `VITE_INTEGRATION_TEST=true`
3. Run the tests
4. Stop the API server

### Test Coverage

- **Unit Tests**: Mock the API client to test component behavior in isolation
- **Integration Tests**: Use the real API to test end-to-end functionality

Both types of tests are important for ensuring reliability.
