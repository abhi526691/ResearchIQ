# Use Python 3.10 base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directories
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install them
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy frontend requirements and install them
COPY frontend/requirements.txt /app/frontend/requirements.txt
RUN pip install --no-cache-dir -r /app/frontend/requirements.txt

# Pre-download NLTK resources
RUN python -m nltk.downloader punkt
# Download NLTK resources
RUN python -m nltk.downloader punkt punkt_tab wordnet stopwords averaged_perceptron_tagger

# Copy backend and frontend code
COPY backend /app/backend
COPY frontend /app/frontend

# Expose ports for Django and Streamlit
EXPOSE 8000 8501

# Start the application with a shell script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]
