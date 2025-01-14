#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Set PYTHONPATH to include backend and frontend
export PYTHONPATH="/app/backend:/app/frontend:$PYTHONPATH"

# Debug: List files in backend and frontend directories
echo "Checking files in /app/backend:"
ls -l /app/backend
echo "Checking files in /app/frontend:"
ls -l /app/frontend

# Start Django backend
echo "Starting Django backend..."
python /app/backend/manage.py migrate
python /app/backend/manage.py runserver 0.0.0.0:8000 &

# Store the PID of the backend process
DJANGO_PID=$!

# Start Streamlit frontend
echo "Starting Streamlit frontend..."
streamlit run /app/frontend/main.py --server.port 8501 --server.address 0.0.0.0 &

# Store the PID of the Streamlit process
STREAMLIT_PID=$!

# Function to handle termination signals and clean up processes
cleanup() {
    echo "Stopping Django backend..."
    kill -SIGTERM "$DJANGO_PID"
    echo "Stopping Streamlit frontend..."
    kill -SIGTERM "$STREAMLIT_PID"
    exit 0
}

# Trap termination signals to call cleanup
trap cleanup SIGINT SIGTERM

# Wait for both processes to complete
wait "$DJANGO_PID"
wait "$STREAMLIT_PID"
