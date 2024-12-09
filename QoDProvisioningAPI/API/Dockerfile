# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies and SQLite CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sqlite3 \
    gcc \
    libsqlite3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY src/ /app/

# Create the data directory for the SQLite database
RUN mkdir -p /data

# Set environment variables
ENV SQLITE_DB_PATH=/data/sqlite.db
