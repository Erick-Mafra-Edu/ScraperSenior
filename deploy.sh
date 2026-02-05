#!/bin/bash
# Deploy script for MCP server

cd ScraperSenior
echo "Stashing local changes..."
git stash

echo "Pulling latest code..."
git pull --rebase

echo "Killing old MCP server process..."
pkill -f 'mcp_server_http' || true
sleep 2

echo "Starting new MCP server..."
nohup python3 apps/mcp-server/mcp_server_http.py > /tmp/mcp_server.log 2>&1 &

sleep 3

echo "Checking if server is running..."
ps aux | grep -E 'mcp_server_http|uvicorn' | grep -v grep

echo "Done!"
