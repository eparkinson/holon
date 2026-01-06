import type {
  Process,
  ProcessSummary,
  RunDetail,
  TraceEvent,
  DeployRequest,
  DeployResponse,
  RunRequest,
  RunResponse,
} from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

class ApiClient {
  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  }

  async deployProcess(data: DeployRequest): Promise<DeployResponse> {
    return this.request<DeployResponse>('/deploy', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async listProcesses(): Promise<ProcessSummary[]> {
    return this.request<ProcessSummary[]>('/projects');
  }

  async getProcess(projectId: string): Promise<Process> {
    return this.request<Process>(`/projects/${projectId}`);
  }

  async triggerRun(
    projectId: string,
    data?: RunRequest
  ): Promise<RunResponse> {
    return this.request<RunResponse>(`/projects/${projectId}/run`, {
      method: 'POST',
      body: JSON.stringify(data || {}),
    });
  }

  async getRunStatus(runId: string): Promise<RunDetail> {
    return this.request<RunDetail>(`/runs/${runId}`);
  }

  async getRunLogs(runId: string): Promise<TraceEvent[]> {
    return this.request<TraceEvent[]>(`/runs/${runId}/logs`);
  }
}

export const apiClient = new ApiClient();
