#!/bin/bash
# Deploy ML Assistant CLI to Docker Hub

set -e

echo "🐳 Deploying ML Assistant CLI to Docker Hub"

# Configuration
DOCKER_USERNAME="santhoshkumar0918"  # Your actual Docker Hub username
IMAGE_NAME="ml-assistant-cli"
VERSION="0.1.0"

# Build the image
echo "🔨 Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .
docker build -t ${IMAGE_NAME}:${VERSION} .

# Tag for Docker Hub
echo "🏷️  Tagging images..."
docker tag ${IMAGE_NAME}:latest ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
docker tag ${IMAGE_NAME}:${VERSION} ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}

# Test the image
echo "🧪 Testing Docker image..."
docker run --rm ${IMAGE_NAME}:latest --help

echo "📋 Images ready for deployment:"
docker images | grep ${IMAGE_NAME}

echo "📤 Ready to push to Docker Hub!"
echo "First login: docker login"
echo "Then push: docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
echo "And: docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}"

# Optional: Push to Docker Hub
read -p "Login and push to Docker Hub now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔐 Logging into Docker Hub..."
    docker login
    
    echo "📤 Pushing to Docker Hub..."
    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest
    docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${VERSION}
    
    echo "✅ Published to Docker Hub!"
    echo "🎉 Users can now run: docker run -it --rm -v \$(pwd):/home/mlcli/workspace ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
fi