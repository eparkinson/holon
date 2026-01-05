import { useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { StatusBadge } from '@/components/StatusBadge';
import { Clock, DollarSign } from 'lucide-react';

export function RunDetailView() {
  const { runId } = useParams<{ runId: string }>();

  // Mock data - will be replaced with real API data
  const run = {
    id: runId,
    project_id: '1',
    status: 'COMPLETED' as const,
    started_at: '2024-01-05T12:00:00Z',
    ended_at: '2024-01-05T12:05:00Z',
  };

  const traceEvents = [
    {
      step_id: 'gather_intelligence',
      status: 'COMPLETED' as const,
      timestamp: '2024-01-05T12:02:00Z',
      metrics: {
        latency_ms: 2000,
        cost_usd: 0.05,
      },
    },
    {
      step_id: 'draft_strategy',
      status: 'COMPLETED' as const,
      timestamp: '2024-01-05T12:05:00Z',
      metrics: {
        latency_ms: 3000,
        cost_usd: 0.08,
      },
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Run Details</h1>
        <p className="text-muted-foreground">
          Execution trace and debugging information
        </p>
      </div>

      {/* Run Info */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Run {runId}</CardTitle>
              <CardDescription>
                Started {new Date(run.started_at).toLocaleString()}
              </CardDescription>
            </div>
            <StatusBadge status={run.status} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">
                Duration: {run.ended_at ? '5m 0s' : 'Running...'}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">Cost: $0.13</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Trace Events */}
      <Card>
        <CardHeader>
          <CardTitle>Execution Timeline</CardTitle>
          <CardDescription>
            Step-by-step workflow execution details
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {traceEvents.map((event) => (
              <div
                key={event.step_id}
                className="flex items-start space-x-4 border-l-2 border-primary pl-4 py-2"
              >
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-semibold">{event.step_id}</h4>
                    <StatusBadge status={event.status} />
                  </div>
                  <div className="mt-2 flex items-center space-x-4 text-sm text-muted-foreground">
                    <span>Latency: {event.metrics.latency_ms}ms</span>
                    <span>Cost: ${event.metrics.cost_usd}</span>
                    <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
