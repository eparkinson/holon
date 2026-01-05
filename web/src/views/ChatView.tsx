import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { MessageSquare } from 'lucide-react';

export function ChatView() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Chat / Playground</h1>
        <p className="text-muted-foreground">
          Interact with agents directly or test workflows
        </p>
      </div>

      <Card className="h-[600px]">
        <CardHeader>
          <CardTitle>Agent Chat</CardTitle>
          <CardDescription>
            Chat interface will be integrated here
          </CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-[500px]">
          <div className="text-center">
            <MessageSquare className="mx-auto h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-semibold">Chat Interface</h3>
            <p className="text-sm text-muted-foreground mt-2">
              DeepChat integration coming soon
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
