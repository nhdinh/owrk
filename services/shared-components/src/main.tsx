import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

// This is a placeholder app for the shared components host
// The actual components will be consumed via Module Federation

function App() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Shared Components Host</h1>
        <p className="text-muted-foreground">
          This service exposes shared components via Module Federation.
        </p>
        <div className="mt-6 text-sm">
          <p>Exposed modules:</p>
          <ul className="mt-2 space-y-1">
            <li><code className="bg-muted px-2 py-1 rounded">shared_components/AppSidebar</code></li>
            <li><code className="bg-muted px-2 py-1 rounded">shared_components/AppLayout</code></li>
          </ul>
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
