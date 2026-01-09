import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, X, FileText } from 'lucide-react';
import { apiClient } from '@/services/api';
import type { DeployRequest } from '@/types/api';

interface DeployDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function DeployDialog({ isOpen, onClose, onSuccess }: DeployDialogProps) {
  const [name, setName] = useState('');
  const [configYaml, setConfigYaml] = useState('');
  const [envVars, setEnvVars] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setConfigYaml(content);
        
        // Extract project name from YAML if not already set
        if (!name) {
          const projectMatch = content.match(/project:\s*["']?([^"'\n]+)["']?/);
          if (projectMatch) {
            setName(projectMatch[1]);
          }
        }
      };
      reader.readAsText(file);
    }
  };

  const parseEnvVars = (envString: string): Record<string, string> | undefined => {
    if (!envString.trim()) return undefined;
    
    const envVarsObj: Record<string, string> = {};
    const lines = envString.split('\n');
    
    for (const line of lines) {
      const trimmedLine = line.trim();
      if (trimmedLine && !trimmedLine.startsWith('#')) {
        const [key, ...valueParts] = trimmedLine.split('=');
        if (key && valueParts.length > 0) {
          envVarsObj[key.trim()] = valueParts.join('=').trim();
        }
      }
    }
    
    return Object.keys(envVarsObj).length > 0 ? envVarsObj : undefined;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError('Process name is required');
      return;
    }

    if (!configYaml.trim()) {
      setError('YAML configuration is required');
      return;
    }

    setIsSubmitting(true);

    try {
      const request: DeployRequest = {
        name: name.trim(),
        config_yaml: configYaml,
        env_vars: parseEnvVars(envVars),
      };

      await apiClient.deployProcess(request);
      
      // Reset form
      setName('');
      setConfigYaml('');
      setEnvVars('');
      setError(null);
      
      // Notify parent of success
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to deploy process');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    if (!isSubmitting) {
      setName('');
      setConfigYaml('');
      setEnvVars('');
      setError(null);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
          <div>
            <CardTitle>Deploy New Process</CardTitle>
            <CardDescription>Upload or paste your holon.yaml configuration</CardDescription>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClose}
            disabled={isSubmitting}
          >
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>
        
        <CardContent className="flex-1 overflow-auto pt-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Process Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Process Name *</Label>
              <Input
                id="name"
                placeholder="e.g., Daily-Briefing"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isSubmitting}
                required
              />
            </div>

            {/* File Upload */}
            <div className="space-y-2">
              <Label htmlFor="file-upload">Upload YAML File</Label>
              <div className="flex items-center gap-2">
                <Input
                  id="file-upload"
                  type="file"
                  accept=".yaml,.yml"
                  onChange={handleFileUpload}
                  disabled={isSubmitting}
                  className="flex-1"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  disabled={isSubmitting}
                  onClick={() => {
                    const input = document.getElementById('file-upload') as HTMLInputElement;
                    input?.click();
                  }}
                >
                  <Upload className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* YAML Content */}
            <div className="space-y-2">
              <Label htmlFor="config-yaml">
                YAML Configuration *
                {configYaml && (
                  <span className="ml-2 text-xs text-muted-foreground">
                    ({configYaml.split('\n').length} lines)
                  </span>
                )}
              </Label>
              <Textarea
                id="config-yaml"
                placeholder="Paste your holon.yaml content here..."
                value={configYaml}
                onChange={(e) => setConfigYaml(e.target.value)}
                disabled={isSubmitting}
                required
                className="font-mono text-xs min-h-[300px]"
              />
            </div>

            {/* Environment Variables (Optional) */}
            <div className="space-y-2">
              <Label htmlFor="env-vars">
                Environment Variables (Optional)
                <span className="ml-2 text-xs text-muted-foreground font-normal">
                  One per line: KEY=value
                </span>
              </Label>
              <Textarea
                id="env-vars"
                placeholder="API_KEY=your_key_here&#10;WEBHOOK_TOKEN=token123"
                value={envVars}
                onChange={(e) => setEnvVars(e.target.value)}
                disabled={isSubmitting}
                className="font-mono text-xs min-h-[100px]"
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                {error}
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-4 border-t">
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>Deploying...</>
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Deploy Process
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
