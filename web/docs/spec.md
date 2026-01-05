# Holon Dashboard Technical Specification

## 1. Overview
The Holon Dashboard is a standalone Single Page Application (SPA) that provides observability and control over the Holon Engine. It allows users to monitor running processes, inspect trace logs, and interact with agents via a chat interface.

## 2. Technology Stack
*   **Framework:** [React](https://react.dev/) (via [Vite](https://vitejs.dev/))
*   **Language:** TypeScript
*   **Styling:** [TailwindCSS](https://tailwindcss.com/) + [shadcn/ui](https://ui.shadcn.com/) (for accessible components)
*   **State Management:** [TanStack Query](https://tanstack.com/query/latest) (React Query) for server state.
*   **Chat Component:** [DeepChat](https://deepchat.dev/) (or Vercel AI SDK) for the embedded chat interface.
*   **Icons:** [Lucide React](https://lucide.dev/)

## 3. Architecture

```mermaid
graph LR
    User -->|Browser| Dashboard[React SPA]
    Dashboard -->|REST (TanStack Query)| EngineAPI[Engine REST API]
    Dashboard -->|WebSocket| EngineWS[Engine WS]
    EngineWS -->|Stream| ChatWidget[DeepChat Component]
```

## 4. Core Views (Routes)

### 4.1 Dashboard Home (`/`)
*   **Goal:** High-level system health.
*   **Components:**
    *   **Stats Cards:** Active Runs, Failed Runs (Last 24h), Total Cost.
    *   **Recent Activity Table:** List of the last 10 runs with status badges.

### 4.2 Projects List (`/projects`)
*   **Goal:** Manage deployed configurations.
*   **Components:**
    *   **Project Card:** Name, Last Deployed, Trigger Type.
    *   **"Run Now" Button:** Manually trigger a project.
    *   **Config Viewer:** Read-only code block showing the `holon.yaml`.

### 4.3 Run Detail / Trace View (`/runs/:id`)
*   **Goal:** Debug a specific execution.
*   **Components:**
    *   **Waterfall Graph:** Visual timeline of steps (Scatter-Gather visualization).
    *   **Step Detail Panel:** Click a step to see Input, Output, Latency, and Cost.
    *   **Logs Tab:** Raw text logs.

### 4.4 Chat / Playground (`/chat`)
*   **Goal:** Interact with agents directly or "Human-in-the-Loop".
*   **Components:**
    *   **DeepChat Widget:** Connected to a specific agent or workflow.
    *   **Context Sidebar:** Shows the current "Blackboard" state during the chat.

## 5. API Integration
The dashboard consumes the Engine API defined in `engine/docs/swagger.md`.

*   **Base URL:** `http://localhost:8000/api/v1` (Configurable via `.env`)
*   **Polling:** Uses TanStack Query to poll `/runs/{id}` every 2 seconds while status is `RUNNING`.

## 6. Development Workflow
1.  **Setup:** `npm install`
2.  **Dev Server:** `npm run dev` (Runs on port 3000)
3.  **Build:** `npm run build` (Outputs to `dist/`)

## 7. Future Scope
*   **Visual Editor:** Drag-and-drop builder to generate `holon.yaml`.
*   **Dark Mode:** Toggle theme.
*   **Auth:** Login screen if the Engine requires authentication.
