import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, FileText } from 'lucide-react';
import { useEffect, useState } from 'react';
import { apiClient } from '@/services/api';
import type { ProjectSummary } from '@/types/api';

export function ProjectsView() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const data = await apiClient.listProjects();
        setProjects(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load projects');
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  const handleRunProject = async (projectId: string) => {
    try {
      await apiClient.triggerRun(projectId);
      // Optionally show success message or navigate to run view
    } catch (err) {
      console.error('Failed to trigger run:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-muted-foreground">
            Manage your deployed Holon configurations
          </p>
        </div>
        <Button>
          <FileText className="mr-2 h-4 w-4" />
          Deploy New Project
        </Button>
      </div>

      {/* Projects Grid */}
      {loading ? (
        <div className="text-center py-12">Loading projects...</div>
      ) : error ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center text-red-500">
              <p>Error loading projects: {error}</p>
            </div>
          </CardContent>
        </Card>
      ) : projects.length === 0 ? (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No projects yet</h3>
              <p className="text-sm text-muted-foreground mt-2">
                Get started by deploying your first holon.yaml configuration
              </p>
              <Button className="mt-4">Deploy Project</Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
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
                  <Button size="sm" onClick={() => handleRunProject(project.id)}>
                    <Play className="mr-2 h-3 w-3" />
                    Run
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
