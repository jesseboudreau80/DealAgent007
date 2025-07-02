#!/bin/bash

# Set Python path
export PYTHONPATH=/opt/render/project/src

# Navigate to project directory
cd /opt/render/project/src

# (Optional) install dependencies — remove if handled in buildCommand
# pip install -r requirements.txt

# Start FastAPI backend in the foreground
exec uvicorn service:app --host 0.0.0.0 --port $PORT
