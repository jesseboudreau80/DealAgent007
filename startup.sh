#!/bin/bash

export PYTHONPATH=/workspaces/DealAgent007

# Log file
LOGFILE="./startup.log"

echo "🚀 Starting DealAgent007 - $(date)" > $LOGFILE

# === BACKEND ===
echo "🔧 Starting backend..." >> $LOGFILE
cd /opt/render/project/src
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..." >> $LOGFILE
    pip install -r requirements.txt >> $LOGFILE 2>&1
fi

echo "🌀 Launching backend with uvicorn..." >> $LOGFILE
export PYTHONPATH=$(pwd)
nohup uvicorn service:app --host 0.0.0.0 --port $PORT >> $LOGFILE 2>&1 &

# === FRONTEND ===
echo "🔧 Starting frontend..." >> $LOGFILE
cd ./chat-ui
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node dependencies..." >> $LOGFILE
    npm install >> $LOGFILE 2>&1
fi

echo "🌀 Launching frontend..." >> $LOGFILE
nohup npm start >> $LOGFILE 2>&1 &

echo "✅ All services started. Check $LOGFILE for logs."
