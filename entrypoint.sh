#!/bin/bash

# Start Django backend
echo "Starting Django backend..."
python /app/backend/manage.py migrate
python /app/backend/manage.py runserver 0.0.0.0:8000 &

# Start Streamlit frontend
echo "Starting Streamlit frontend..."
streamlit run /app/frontend/app.py --server.port 8501 --server.address 0.0.0.0
