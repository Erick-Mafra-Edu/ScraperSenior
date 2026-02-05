#!/bin/bash
# Deploy MCP Server with Docker rebuild

cd ScraperSenior

echo "========================================="
echo "Deploying MCP Server with rebuild"
echo "========================================="

echo "Pulling latest code..."
git pull --rebase

echo "Stopping old container..."
podman stop senior-docs-mcp-server || true

echo "Removing old container..."
podman rm senior-docs-mcp-server || true

echo "Building new image..."
podman build -f Dockerfile.mcp -t localhost/senior-docs-mcp:latest .

echo "Starting container..."
podman run -d \
  --name senior-docs-mcp-server \
  -p 8000:8000 \
  --health-cmd='curl -f http://localhost:8000/health || exit 1' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-start-period=15s \
  --health-retries=3 \
  localhost/senior-docs-mcp:latest

echo "Waiting for container to start..."
sleep 5

echo "Container status:"
podman ps | grep senior-docs-mcp

echo "✓ Deploy complete!"
