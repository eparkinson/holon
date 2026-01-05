import { useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { StatusBadge } from '@/components/StatusBadge';
import { Clock, DollarSign } from 'lucide-react';
import { formatDuration } from '@/lib/utils';
import { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import type { RunDetail, TraceEvent } from '@/types/api';

export function RunDetailView() {
  const { runId } = useParams<{ runId: string }>();
  const [run, setRun] = useState<RunDetail | null>(null);
  const [traceEvents, setTraceEvents] = useState<TraceEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRunDetails = async () => {
      if (!runId) return;

      try {
        setLoading(true);
        const [runData, logsData] = await Promise.all([
          apiClient.getRunStatus(runId),
          apiClient.getRunLogs(runId),
        ]);
        setRun(runData);
        setTraceEvents(logsData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load run details');
      } finally {
        setLoading(false);
      }
    };

    fetchRunDetails();
  }, [runId]);

  if (loading) {
    return <div className="text-center py-12">Loading run details...</div>;
  }

  if (error || !run) {
    return (
      <div className="text-center py-12 text-red-500">
        Error: {error || 'Run not found'}
      </div>
    );
  }

  const duration = run.started_at && run.ended_at 
    ? formatDuration(run.started_at, run.ended_at)
    : 'Running...';

  const totalCost = traceEvents.reduce(
    (sum, event) => sum + (event.metrics?.cost_usd || 0),
    0
  );

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
                {run.started_at 
                  ? `Started ${new Date(run.started_at).toLocaleString()}`
                  : 'Not started yet'}
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
                Duration: {duration}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">Cost: ${totalCost.toFixed(2)}</span>
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
          {traceEvents.length === 0 ? (
            <p className="text-sm text-muted-foreground">No trace events yet</p>
          ) : (
            <div className="space-y-4">
              {traceEvents.map((event, idx) => (
                <div
                  key={`${event.step_id}-${event.timestamp}-${idx}`}
                  className="flex items-start space-x-4 border-l-2 border-primary pl-4 py-2"
                >
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold">{event.step_id}</h4>
                      <StatusBadge status={event.status} />
                    </div>
                    <div className="mt-2 flex items-center space-x-4 text-sm text-muted-foreground">
                      {event.metrics?.latency_ms && (
                        <span>Latency: {event.metrics.latency_ms}ms</span>
                      )}
                      {event.metrics?.cost_usd !== undefined && (
                        <span>Cost: ${event.metrics.cost_usd}</span>
                      )}
                      <span>{new Date(event.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
