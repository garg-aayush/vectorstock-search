#!/bin/bash

# Multi-platform Docker build script for Runpod deployment
# This ensures the image works on linux/amd64 (x86_64) architecture

set -e

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-thebigpanda}"
IMAGE_NAME="vectorstock-dashboard"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building multi-platform Docker image for Runpod..."
echo "Image: ${FULL_IMAGE_NAME}"
echo "Platform: linux/amd64"

# Ensure buildx is available
if ! docker buildx version &> /dev/null; then
    echo "Docker buildx not found. Please update Docker Desktop."
    exit 1
fi

# Create builder if it doesn't exist
if ! docker buildx ls | grep -q "mybuilder"; then
    echo "Creating buildx builder..."
    docker buildx create --use --name mybuilder
fi

# Build and push for linux/amd64
echo "Building and pushing image..."
docker buildx build \
    --platform linux/amd64 \
    -t ${FULL_IMAGE_NAME} \
    --push \
    .

echo "✅ Build complete! Image pushed to Docker Hub."
echo "   Image: ${FULL_IMAGE_NAME}"
echo "   Platform: linux/amd64"
echo ""
echo "You can now deploy this image on Runpod without architecture issues!"
