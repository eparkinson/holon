import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { DeepChat } from 'deep-chat-react';

export function ChatView() {
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
            Interactive chat interface for testing agent interactions
          </CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <DeepChat
            style={{
              borderRadius: '0 0 8px 8px',
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
            introMessage={{
              text: 'Welcome to the Holon Agent Playground! This is a skeleton chat interface. In production, this will connect to your configured agents via the Holon Engine.',
            }}
            history={[
              {
                role: 'ai',
                text: 'Hello! I\'m a placeholder agent. Once integrated with the Holon Engine, I\'ll be able to execute workflows and assist you with tasks.',
              },
              {
                role: 'user',
                text: 'What can you do?',
              },
              {
                role: 'ai',
                text: 'Currently, this is a demonstration interface. When connected to the Holon Engine, I will be able to:\n\n• Execute workflow configurations\n• Search and analyze data using configured agents\n• Provide insights from scatter-gather patterns\n• Stream responses in real-time\n\nFor now, you can explore the UI and test the chat interaction.',
              },
            ]}
            demo={true}
          />
        </CardContent>
      </Card>
    </div>
  );
}
