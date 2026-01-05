# Holon Dashboard

The Holon Dashboard is a React-based Single Page Application (SPA) that provides observability and control over the Holon Engine.

## Features

- **Dashboard Home**: System health overview with stats cards and recent activity
- **Projects Management**: Deploy and manage Holon configurations
- **Run Details**: Debug workflow executions with trace visualization
- **Chat Interface**: Interactive agent playground (coming soon)

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: TailwindCSS
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router v6
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
npm install
```

### Development

Start the development server (runs on port 3000):

```bash
npm run dev
```

The dashboard will proxy API requests to `http://localhost:8000` (the Holon Engine).

### Build

Build for production:

```bash
npm run build
```

The output will be in the `dist/` directory.

### Testing

Run tests:

```bash
npm test
```

## Project Structure

```
web/
├── src/
│   ├── components/       # Reusable UI components
│   │   └── ui/          # Base UI components (Button, Card, Badge)
│   ├── views/           # Page-level components
│   ├── services/        # API client
│   ├── types/           # TypeScript type definitions
│   ├── lib/             # Utility functions
│   └── test/            # Test files
├── public/              # Static assets
└── docs/                # Documentation
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Available environment variables:

- `VITE_API_BASE_URL`: Base URL for the Holon Engine API (default: `/api/v1`)

## License

MIT
