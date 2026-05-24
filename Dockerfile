# Use a stable, official Python slim image for production efficiency
FROM python:3.11-slim

# Install system dependencies (ffmpeg is required for Whisper fallback, build-essential for compiling C extensions if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set standard environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8501

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Pre-create folders for persistent data storage
RUN mkdir -p chromadb_data uploads

# Expose Streamlit's port
EXPOSE 8501

# Run the app binding to all interfaces for container routing
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
