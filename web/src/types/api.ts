// API Types based on OpenAPI spec

export interface ProcessSummary {
  id: string;
  name: string;
  created_at: string;
}

export interface Process extends ProcessSummary {
  config_yaml: string;
}

export type RunStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface RunDetail {
  id: string;
  project_id: string;
  status: RunStatus;
  context: Record<string, unknown>;
  started_at: string;
  ended_at?: string;
}

export interface TraceEvent {
  step_id: string;
  // TraceEvent status is limited to terminal states only
  // (steps are only logged once completed or failed)
  status: 'COMPLETED' | 'FAILED';
  input: Record<string, unknown>;
  output: Record<string, unknown>;
  metrics: {
    latency_ms: number;
    cost_usd: number;
  };
  timestamp: string;
}

export interface DeployRequest {
  name: string;
  config_yaml: string;
  env_vars?: Record<string, string>;
}

export interface DeployResponse {
  project_id: string;
  status: string;
}

export interface RunRequest {
  input_context?: Record<string, unknown>;
}

export interface RunResponse {
  run_id: string;
  status: RunStatus;
}
