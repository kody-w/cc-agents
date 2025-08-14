#!/bin/bash

# Deployment script for can_analyze_our_agent

set -e

echo "Deploying can_analyze_our_agent..."

# Build and test
echo "Running tests..."
pytest

echo "Building Docker image..."
docker-compose build

# Deploy based on strategy
DEPLOY_TYPE="simple"

case $DEPLOY_TYPE in
    simple)
        echo "Starting container..."
        docker-compose up -d
        ;;
    
    containerized)
        echo "Deploying to Kubernetes..."
        kubectl apply -f k8s/
        ;;
    
    microservices)
        echo "Deploying with Helm..."
        helm upgrade --install can_analyze_our_agent ./helm-chart
        ;;
    
    *)
        echo "Unknown deployment type: $DEPLOY_TYPE"
        exit 1
        ;;
esac

# Verify deployment
echo "Verifying deployment..."
sleep 5

if curl -f http://localhost:8000/health; then
    echo "Deployment successful!"
else
    echo "Deployment failed!"
    exit 1
fi

echo "Agent can_analyze_our_agent deployed successfully!"
