import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, X, FileText } from 'lucide-react';
import { apiClient } from '@/services/api';
import type { DeployRequest } from '@/types/api';

// Validation pattern for environment variable keys
const ENV_VAR_KEY_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/;

// Pattern for extracting name from YAML
const YAML_NAME_PATTERN = /name:\s*["']?([^"'\n]+)["']?/;

interface DeployDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function DeployDialog({ isOpen, onClose, onSuccess }: DeployDialogProps) {
  const [configYaml, setConfigYaml] = useState('');
  const [envVars, setEnvVars] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [extractedName, setExtractedName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const extractNameFromYaml = (yaml: string): string | null => {
    const nameMatch = yaml.match(YAML_NAME_PATTERN);
    return nameMatch ? nameMatch[1].trim() : null;
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setConfigYaml(content);
        
        // Extract name from YAML
        const name = extractNameFromYaml(content);
        if (name) {
          setExtractedName(name);
          setShowConfirmation(true);
        } else {
          setError('Could not find "name:" field in YAML configuration');
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
        const equalIndex = trimmedLine.indexOf('=');
        if (equalIndex > 0) {
          const key = trimmedLine.substring(0, equalIndex).trim();
          const value = trimmedLine.substring(equalIndex + 1).trim();
          
          // Validate key follows environment variable naming conventions
          if (key && ENV_VAR_KEY_PATTERN.test(key)) {
            envVarsObj[key] = value;
          }
        }
      }
    }
    
    return Object.keys(envVarsObj).length > 0 ? envVarsObj : undefined;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!extractedName) {
      setError('Process name is required. Make sure your YAML contains a "name:" field.');
      return;
    }

    if (!configYaml.trim()) {
      setError('YAML configuration is required');
      return;
    }

    setIsSubmitting(true);

    try {
      const request: DeployRequest = {
        name: extractedName,
        config_yaml: configYaml,
        env_vars: parseEnvVars(envVars),
      };

      await apiClient.deployProcess(request);
      
      // Reset form
      setConfigYaml('');
      setEnvVars('');
      setError(null);
      setShowConfirmation(false);
      setExtractedName(null);
      
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
      setConfigYaml('');
      setEnvVars('');
      setError(null);
      setShowConfirmation(false);
      setExtractedName(null);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4 border-b">
          <div>
            <CardTitle>{showConfirmation ? 'Confirm Deployment' : 'Deploy New Process'}</CardTitle>
            <CardDescription>
              {showConfirmation 
                ? 'Review and confirm your deployment' 
                : 'Upload or paste your holon.yaml configuration'}
            </CardDescription>
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
          {!showConfirmation ? (
            <form onSubmit={(e) => {
              e.preventDefault();
              // Extract name from pasted YAML
              if (configYaml) {
                const name = extractNameFromYaml(configYaml);
                if (name) {
                  setExtractedName(name);
                  setShowConfirmation(true);
                  setError(null);
                } else {
                  setError('Could not find "name:" field in YAML configuration');
                }
              }
            }} className="space-y-6">
              {/* File Upload */}
              <div className="space-y-2">
                <Label htmlFor="file-upload">Upload YAML File</Label>
                <div className="flex items-center gap-2">
                  <Input
                    ref={fileInputRef}
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
                    onClick={() => fileInputRef.current?.click()}
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
                <Button type="submit" disabled={isSubmitting || !configYaml}>
                  Continue
                </Button>
              </div>
            </form>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Confirmation Screen */}
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-muted/50 border">
                  <h3 className="font-semibold mb-2">Process Name</h3>
                  <p className="text-2xl font-bold">{extractedName}</p>
                </div>

                <div className="space-y-2">
                  <h3 className="font-semibold">Configuration Preview</h3>
                  <div className="bg-slate-950 text-slate-50 p-4 rounded-md overflow-x-auto text-xs font-mono leading-relaxed border border-slate-800 max-h-[300px] overflow-y-auto">
                    {configYaml.split('\n').map((line, i) => (
                      <div key={i} className="text-slate-300">{line || ' '}</div>
                    ))}
                  </div>
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
                    placeholder={`API_KEY=your_key_here\nWEBHOOK_TOKEN=token123`}
                    value={envVars}
                    onChange={(e) => setEnvVars(e.target.value)}
                    disabled={isSubmitting}
                    className="font-mono text-xs min-h-[100px]"
                  />
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                  {error}
                </div>
              )}

              {/* Actions */}
              <div className="flex justify-between gap-2 pt-4 border-t">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowConfirmation(false);
                    setExtractedName(null);
                  }}
                  disabled={isSubmitting}
                >
                  Back
                </Button>
                <div className="flex gap-2">
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
              </div>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
