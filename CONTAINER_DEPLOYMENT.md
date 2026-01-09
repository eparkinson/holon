# Unified Container Deployment

This guide explains how to deploy Holon as a single Docker container containing both the engine and web app.

## Quick Start

```bash
# Start Holon in a single container
./scripts/start_local.sh --container
```

This will:
1. Build the web app (if not already built)
2. Create a Docker image with both engine and web app
3. Start the container exposing port 80
4. Run both services using supervisord

Access the application:
- **Web Dashboard:** http://localhost
- **API Swagger UI:** http://localhost/docs

## How It Works

The unified container uses:
- **supervisord**: Process manager to run both engine and nginx
- **nginx**: Web server to serve the React app and proxy API requests
- **Python engine**: FastAPI backend on port 8000 (internal)
- **Port 80**: Public-facing port for both web and API

## Architecture

```
┌─────────────────────────────────────────┐
│     Holon Unified Container (Port 80)    │
├─────────────────────────────────────────┤
│  nginx (Port 80)                         │
│  ├─ Serves: /          → React App       │
│  └─ Proxies: /api/*    → Engine:8000     │
├─────────────────────────────────────────┤
│  Holon Engine (Port 8000 - internal)     │
│  └─ FastAPI Backend                      │
├─────────────────────────────────────────┤
│  supervisor                              │
│  └─ Manages both nginx and engine        │
└─────────────────────────────────────────┘
```

## Manual Build

If you want to build manually:

```bash
# 1. Build the web app first
cd web
npm install
npm run build
cd ..

# 2. Build the Docker image
docker build -f Dockerfile.unified -t holon-unified:latest .

# 3. Run the container
docker run -d \
    --name holon-unified \
    -p 80:80 \
    -v $(pwd)/holon_data:/app/holon_data \
    holon-unified:latest
```

## Stopping the Container

```bash
# Using the script
./scripts/stop_local.sh

# Or manually
docker stop holon-unified
docker rm holon-unified
```

## Viewing Logs

```bash
# All logs
docker logs -f holon-unified

# Engine logs only
docker exec holon-unified tail -f /var/log/supervisor/engine.out.log

# Nginx logs only
docker exec holon-unified tail -f /var/log/supervisor/nginx.out.log
```

## Configuration Files

- **Dockerfile.unified**: Main Dockerfile for the container
- **nginx.conf**: Nginx configuration for serving web app and proxying API
- **supervisord.conf**: Process manager configuration
- **scripts/start_local.sh --container**: Launch script

## Differences from Docker Compose

| Feature | Docker Compose (--docker) | Unified Container (--container) |
|---------|---------------------------|--------------------------------|
| Containers | 2 separate containers | 1 unified container |
| Ports | 3000 (web), 8000 (API) | 80 (both) |
| Web Access | http://localhost:3000 | http://localhost |
| API Access | http://localhost:8000 | http://localhost/api |
| Process Manager | Docker Compose | supervisord |
| Production Ready | Development | Closer to production |

## Production Deployment

For production, consider:
1. Using a reverse proxy (e.g., Traefik, Caddy) for SSL termination
2. Setting up environment variables for API keys
3. Configuring persistent volumes for `holon_data`
4. Using container orchestration (e.g., Kubernetes, Docker Swarm)

Example with SSL:
```bash
docker run -d \
    --name holon-unified \
    -p 80:80 \
    -v $(pwd)/holon_data:/app/holon_data \
    -e ANTHROPIC_API_KEY=your_key_here \
    holon-unified:latest
```

## Troubleshooting

### Container won't start
```bash
# Check container logs
docker logs holon-unified

# Check if ports are already in use
sudo lsof -i :80
```

### API requests fail
```bash
# Verify nginx is proxying correctly
docker exec holon-unified curl http://localhost/api/v1/version

# Check nginx configuration
docker exec holon-unified nginx -t
```

### Engine not responding
```bash
# Check engine logs
docker exec holon-unified tail -f /var/log/supervisor/engine.err.log

# Restart the engine process
docker exec holon-unified supervisorctl restart engine
```
