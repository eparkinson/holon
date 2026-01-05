import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play, FileText } from 'lucide-react';

export function ProjectsView() {
  // Mock data - will be replaced with real API data
  const projects = [
    {
      id: '1',
      name: 'Daily Market Briefing',
      created_at: '2024-01-01T00:00:00Z',
      triggerType: 'Schedule',
    },
  ];

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
      {projects.length === 0 ? (
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
                  Trigger: {project.triggerType}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    Created {new Date(project.created_at).toLocaleDateString()}
                  </span>
                  <Button size="sm">
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
