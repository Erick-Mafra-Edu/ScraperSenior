#!/bin/bash
# Deploy MCP Server - Rebuild Docker container

set -e

cd ScraperSenior

echo "==============================================="
echo "🚀 Deploying MCP Server Updates"
echo "==============================================="

# Pull latest
echo "📥 Pulling latest code..."
git pull --rebase

# Stop old container
echo "⏹️  Stopping old container..."
podman stop senior-docs-mcp-server 2>/dev/null || true
sleep 1

# Remove old container
echo "🗑️  Removing old container..."
podman rm senior-docs-mcp-server 2>/dev/null || true

# Build image
echo "🔨 Building Docker image..."
podman build -f Dockerfile.mcp -t senior-docs-mcp:latest .

# Run new container
echo "▶️  Starting new container..."
podman run -d \
  --name senior-docs-mcp-server \
  -p 8000:8000 \
  -e OPENAPI_HOST=0.0.0.0 \
  -e OPENAPI_PORT=8000 \
  -e LOG_LEVEL=INFO \
  senior-docs-mcp:latest

# Wait for startup
echo "⏳ Waiting for container to start..."
sleep 5

# Check status
echo ""
echo "📋 Container Status:"
podman ps | grep senior-docs-mcp

echo ""
echo "📊 Recent Logs:"
podman logs senior-docs-mcp-server | tail -10

# Test endpoint
echo ""
echo "🧪 Testing /health endpoint..."
curl -s http://localhost:8000/health | jq . 2>/dev/null || echo "Health check failed"

echo ""
echo "==============================================="
echo "✅ Deploy complete!"
echo "==============================================="
