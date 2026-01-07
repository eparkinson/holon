import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { DeepChat } from 'deep-chat-react';
import { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import type { ProcessSummary } from '@/types/api';
import { Select } from '@/components/ui/select';

export function ChatView() {
  const [processes, setProcesses] = useState<ProcessSummary[]>([]);
  const [selectedProcessId, setSelectedProcessId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadProcesses = async () => {
      try {
        const data = await apiClient.listProcesses();
        setProcesses(data);
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load processes');
        setLoading(false);
      }
    };
    loadProcesses();
  }, []);

  // Get WebSocket URL based on current API URL
  const getWebSocketUrl = (projectId: string) => {
    const apiUrl = import.meta.env.VITE_API_BASE_URL || window.location.origin + '/api/v1';
    const wsProtocol = apiUrl.startsWith('https') ? 'wss' : 'ws';
    const wsBaseUrl = apiUrl.replace(/^https?:\/\//, '').replace(/\/api\/v1$/, '');
    return `${wsProtocol}://${wsBaseUrl}/api/v1/projects/${projectId}/chat`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Chat / Playground</h1>
        <p className="text-muted-foreground">
          Interact with agents directly or test workflows
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Agent Chat</CardTitle>
          <CardDescription>
            Select a deployed process to chat with
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <label className="text-sm font-medium">Process:</label>
            <Select
              value={selectedProcessId}
              onChange={(e) => setSelectedProcessId(e.target.value)}
              disabled={loading}
              className="w-[300px]"
            >
              <option value="">Select a process...</option>
              {processes.map((process) => (
                <option key={process.id} value={process.id}>
                  {process.name}
                </option>
              ))}
            </Select>
          </div>

          {error && (
            <div className="text-sm text-red-600 p-3 bg-red-50 rounded-md">
              {error}
            </div>
          )}

          {!selectedProcessId && !loading && (
            <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-md">
              Please select a deployed process to start chatting.
            </div>
          )}

          {selectedProcessId && (
            <div className="border rounded-lg overflow-hidden">
              <DeepChat
                key={selectedProcessId}
                style={{
                  width: '100%',
                  height: '600px',
                }}
                messageStyles={{
                  default: {
                    shared: {
                      bubble: {
                        backgroundColor: 'unset',
                        marginTop: '10px',
                        marginBottom: '10px',
                        boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
                      },
                    },
                    user: {
                      bubble: {
                        background: 'linear-gradient(130deg, #2870EA 20%, #1B4AEF 77.5%)',
                      },
                    },
                    ai: {
                      bubble: {
                        background: '#f3f4f6',
                        color: '#374151',
                      },
                    },
                  },
                }}
                textInput={{
                  placeholder: {
                    text: 'Ask a question or send a command to the agent...',
                    style: { color: '#9ca3af' },
                  },
                  styles: {
                    container: {
                      borderRadius: '20px',
                      border: '1px solid #e5e7eb',
                      width: '78%',
                      marginLeft: '-15px',
                      boxShadow: 'unset',
                    },
                  },
                }}
                connect={{
                  url: getWebSocketUrl(selectedProcessId),
                  websocket: true,
                } as Record<string, unknown>}
                requestBodyLimits={{
                  maxMessages: -1,
                }}
                introMessage={{
                  text: 'Connected to the Holon process. Send a message to start chatting!',
                }}
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
