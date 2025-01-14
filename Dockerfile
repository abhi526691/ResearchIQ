# Use Python 3.10 base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set global working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install backend dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Copy and install frontend dependencies
COPY frontend/requirements.txt /app/frontend/requirements.txt
WORKDIR /app/frontend
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLTK resources
RUN python -m nltk.downloader punkt punkt_tab wordnet stopwords averaged_perceptron_tagger

# Copy backend and frontend code
COPY backend /app/backend
COPY frontend /app/frontend

# Expose ports for Django and Streamlit
EXPOSE 8000 8501

# Add and set permissions for entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set backend as the final working directory
WORKDIR /app/backend

# Use the entrypoint script
CMD ["/app/entrypoint.sh"]
