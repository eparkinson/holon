import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from '@/components/Layout';
import { DashboardView } from '@/views/DashboardView';
import { ProcessesView } from '@/views/ProcessesView';
import { RunDetailView } from '@/views/RunDetailView';
import { ChatView } from '@/views/ChatView';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardView />} />
            <Route path="processes" element={<ProcessesView />} />
            <Route path="runs/:runId" element={<RunDetailView />} />
            <Route path="chat" element={<ChatView />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
