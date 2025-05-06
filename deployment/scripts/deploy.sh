#!/bin/bash

# Exit on error
set -e

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "Error: .env file not found"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p config

# Check for secrets.json
if [ ! -f config/secrets.json ]; then
    echo "Error: secrets.json not found in config directory"
    exit 1
fi

# Deploy the application
echo "Deploying PDS Data API..."
docker compose -f deployment/config/docker-compose.prod.yml up -d --build

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker compose -f deployment/config/docker-compose.prod.yml ps | grep -q "Up"; then
    echo "Deployment successful!"
    echo "Application is available at http://localhost:8000"
else
    echo "Error: Services failed to start"
    exit 1
fi 