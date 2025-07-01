#!/bin/bash

echo "🟢 Installing frontend dependencies..."
cd /workspaces/DealAgent007/chat-ui
npm install

echo "🟢 Starting React frontend (background)..."
npm start &

echo "🟢 Starting FastAPI backend..."
cd /workspaces/DealAgent007
uvicorn src.service.service:app --reload --host 0.0.0.0 --port 8000
