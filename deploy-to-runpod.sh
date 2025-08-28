#!/bin/bash

# VectorStock Dashboard Deployment Script for Runpod
# This script builds and deploys the dashboard to Runpod

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}VectorStock Dashboard - Runpod Deployment${NC}"
echo "========================================="

# Configuration
DOCKER_USERNAME="${DOCKER_USERNAME:-thebigpanda}"
IMAGE_NAME="vectorstock-dashboard"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
fi

# Step 1: Build Docker image
echo -e "\n${YELLOW}Step 1: Building Docker image...${NC}"
docker build -t ${FULL_IMAGE_NAME} .

# Step 2: Test locally (optional)
echo -e "\n${YELLOW}Step 2: Testing locally (optional)...${NC}"
read -p "Do you want to test the image locally first? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting local test..."
    docker run -d --name vectorstock-test -p 8501:8501 -v $(pwd)/search_results:/app/search_results:ro ${FULL_IMAGE_NAME}
    echo -e "${GREEN}Dashboard is running at http://localhost:8501${NC}"
    echo "Press Enter to stop the test and continue deployment..."
    read
    docker stop vectorstock-test
    docker rm vectorstock-test
fi

# Step 3: Push to Docker Hub
echo -e "\n${YELLOW}Step 3: Pushing to Docker Hub...${NC}"
echo "Please ensure you're logged in to Docker Hub"
docker login
docker push ${FULL_IMAGE_NAME}

# Step 4: Create volume for search results
echo -e "\n${YELLOW}Step 4: Preparing deployment files...${NC}"
# Create a tar file with search results
tar -czf search_results.tar.gz search_results/

# Step 5: Update Runpod template
echo -e "\n${YELLOW}Step 5: Updating Runpod template...${NC}"
sed -i.bak "s|your-dockerhub-username/vectorstock-dashboard:latest|${FULL_IMAGE_NAME}|g" runpod-template.json

echo -e "\n${GREEN}Deployment preparation complete!${NC}"
echo -e "\nNext steps:"
echo -e "1. Go to https://www.runpod.io/console/deploy"
echo -e "2. Click 'Deploy Custom Template'"
echo -e "3. Upload the ${YELLOW}runpod-template.json${NC} file"
echo -e "4. Configure the following:"
echo -e "   - GPU: ${YELLOW}None needed${NC} (CPU only is sufficient)"
echo -e "   - vCPU: ${YELLOW}2-4 cores${NC}"
echo -e "   - RAM: ${YELLOW}4-8 GB${NC}"
echo -e "   - Storage: ${YELLOW}10 GB${NC}"
echo -e "5. Deploy the pod"
echo -e "6. Once running, access via the public IP on port ${YELLOW}8501${NC}"
echo -e "\nNote: This is a public dashboard with no authentication."
echo -e "For production use, consider:"
echo -e "- Setting up a custom domain"
echo -e "- Configuring HTTPS with Let's Encrypt"
