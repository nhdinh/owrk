import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
// @ts-ignore - Module Federation remote import
import { AuthProvider } from 'shared_components/AuthContext';
import Dashboard from './pages/Dashboard';
import './index.css';

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
      <AuthProvider apiBaseUrl="http://localhost:8000">
        <BrowserRouter basename="/dashboard">
          <Dashboard />
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
