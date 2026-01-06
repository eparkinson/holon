import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, FileText, Eye, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import type { ProcessSummary } from '@/types/api';

// Syntax highlighter component
const YamlViewer = ({ content }: { content: string }) => {
  if (!content) {
    return <div className="p-4 text-muted-foreground italic">No configuration content found</div>;
  }
  // Simple syntax highlighting
  const lines = content.split('\n');
  return (
    <div className="bg-slate-950 text-slate-50 p-4 rounded-md overflow-x-auto text-sm font-mono leading-relaxed border border-slate-800 whitespace-pre">
      {lines.map((line, i) => {
        // Very basic coloring logic
        const isComment = line.trim().startsWith('#');
        const keyMatch = line.match(/^(\s*)([^:]+)(:)(.*)$/);
        
        if (isComment) {
          return <div key={i} className="text-slate-500">{line}</div>;
        }
        
        if (keyMatch) {
          const [, indent, key, colon, val] = keyMatch;
          return (
            <div key={i}>
              <span>{indent}</span>
              <span className="text-blue-400 font-semibold">{key}</span>
              <span className="text-slate-400">{colon}</span>
              <span className="text-emerald-400">{val}</span>
            </div>
          );
        }
        
        return <div key={i} className="text-slate-300">{line}</div>;
      })}
    </div>
  );
};

export function ProcessesView() {
  const [processes, setProcesses] = useState<ProcessSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // New state for modal
  const [selectedProcess, setSelectedProcess] = useState<{name: string, yaml: string} | null>(null);
  const [viewLoading, setViewLoading] = useState(false);

  useEffect(() => {
    const fetchProcesses = async () => {
      try {
        setLoading(true);
        const data = await apiClient.listProcesses();
        setProcesses(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load processes');
      } finally {
        setLoading(false);
      }
    };

    fetchProcesses();
  }, []);

  const handleRunProcess = async (projectId: string) => {
    try {
      await apiClient.triggerRun(projectId);
      // Optionally show success message or navigate to run view
    } catch (err) {
      console.error('Failed to trigger run:', err);
    }
  };

  const handleViewConfig = async (projectId: string, name: string) => {
    try {
      setViewLoading(true);
      const process = await apiClient.getProcess(projectId);
      setSelectedProcess({ name, yaml: process.config_yaml });
    } catch (err) {
      console.error('Failed to load process config', err);
    } finally {
      setViewLoading(false);
    }
  };

  return (
    <div className="space-y-6 relative">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Processes</h1>
          <p className="text-muted-foreground">
            Manage your deployed Holon configurations
          </p>
        </div>
        <Button>
          <FileText className="mr-2 h-4 w-4" />
          Deploy New Process
        </Button>
      </div>

      {/* Processes Grid */}
      {loading ? (
        <div className="text-center py-12">Loading processes...</div>
      ) : error ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-red-500">
              <p>Error loading processes: {error}</p>
            </div>
          </CardContent>
        </Card>
      ) : processes.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No processes yet</h3>
              <p className="text-sm text-muted-foreground mt-2">
                Get started by deploying your first holon.yaml configuration
              </p>
              <Button className="mt-4">Deploy Process</Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {processes.map((project) => (
            <Card key={project.id}>
              <CardHeader>
                <CardTitle>{project.name}</CardTitle>
                <CardDescription>
                  Created {new Date(project.created_at).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    ID: {project.id.substring(0, 8)}...
                  </span>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleViewConfig(project.id, project.name)} disabled={viewLoading}>
                        <Eye className="mr-2 h-3 w-3" />
                        View
                    </Button>
                    <Button size="sm" onClick={() => handleRunProcess(project.id)}>
                        <Play className="mr-2 h-3 w-3" />
                        Run
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
      
      {/* Modal Overlay */}
      {selectedProcess && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-background rounded-lg shadow-lg w-full max-w-6xl max-h-[90vh] flex flex-col border">
                <div className="p-4 border-b flex items-center justify-between">
                    <h2 className="text-lg font-semibold">{selectedProcess.name} Configuration</h2>
                    <Button variant="ghost" size="icon" onClick={() => setSelectedProcess(null)}>
                        <X className="h-4 w-4" />
                    </Button>
                </div>
                <div className="p-0 overflow-hidden flex-1 relative min-h-[600px]">
                    <div className="absolute inset-0 overflow-auto p-4 bg-slate-950">
                        <YamlViewer content={selectedProcess.yaml} />
                    </div>
                </div>
                <div className="p-4 border-t bg-muted/20 flex justify-end">
                    <Button variant="secondary" onClick={() => setSelectedProcess(null)}>Close</Button>
                </div>
            </div>
        </div>
      )}
    </div>
  );
}
