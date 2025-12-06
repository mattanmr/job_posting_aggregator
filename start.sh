#!/bin/bash

# Job Posting Aggregator - Quick Start Guide

echo "🚀 Job Posting Aggregator - Quick Start"
echo "======================================="
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi

cd "$(dirname "$0")"

echo "📦 Building Docker images..."
docker-compose build

echo ""
echo "🏃 Starting services..."
docker-compose up -d

echo ""
sleep 3

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend running at http://localhost:8000"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Check frontend
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend running at http://localhost:5173"
else
    echo "⚠️  Frontend may take a moment to fully initialize"
fi

echo ""
echo "📚 Useful endpoints:"
echo "  - Frontend: http://localhost:5173"
echo "  - API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "🛑 To stop: docker-compose down"
echo "📋 To view logs: docker-compose logs -f [backend|frontend]"
