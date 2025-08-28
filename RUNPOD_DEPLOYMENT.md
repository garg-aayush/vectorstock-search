# VectorStock Dashboard - Runpod Deployment Guide

This guide will walk you through deploying the VectorStock Dashboard as a public endpoint on Runpod.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Deployment Steps](#detailed-deployment-steps)
- [Public Access Configuration](#public-access-configuration)
- [Sharing the Dashboard](#sharing-the-dashboard)
- [Maintenance and Updates](#maintenance-and-updates)
- [Troubleshooting](#troubleshooting)

## Prerequisites

1. **Runpod Account**: Sign up at [runpod.io](https://www.runpod.io)
2. **Docker Hub Account**: For hosting the container image
3. **Docker Desktop**: Installed on your local machine
4. **Your VectorStock search results**: In the `search_results/` directory

## Quick Start

```bash
# 1. Build and push the Docker image
export DOCKER_USERNAME="your-dockerhub-username"
./deploy-to-runpod.sh

# 2. Deploy on Runpod using the generated template
# 3. Configure authentication (see Security section)
```

## Detailed Deployment Steps

### Step 1: Prepare Your Docker Image

1. **Build the Docker image**:
   ```bash
   docker build -t thebigpanda/vectorstock-dashboard:latest .
   ```

2. **Test locally** (optional):
   ```bash
   docker-compose up -d
   # Visit http://localhost:8501
   ```

3. **Push to Docker Hub**:
   ```bash
   docker login
   docker push thebigpanda/vectorstock-dashboard:latest
   ```

### Step 2: Deploy on Runpod

1. **Login to Runpod Console**: https://www.runpod.io/console

2. **Deploy a New Pod**:
   - Click "Deploy" → "Pods" → "GPU Cloud" or "CPU Cloud"
   - For this dashboard, **CPU Cloud is sufficient** (cheaper option)

3. **Configure the Pod**:
   - **Container Image**: `thebigpanda/vectorstock-dashboard:latest`
   - **Container Disk**: 10 GB
   - **Volume Disk**: 10 GB (for persistent data)
   - **Expose HTTP Ports**: `8501`
   - **vCPU**: 2-4 cores
   - **RAM**: 4-8 GB
   - **GPU**: Not required (select "CPU Pod" for cost savings)

4. **Environment Variables**: No authentication required for public access

5. **Deploy the Pod**:
   - Click "Deploy On-Demand" or "Deploy Spot" (cheaper but can be interrupted)
   - Wait for the pod to start (2-3 minutes)

### Step 3: Access Your Dashboard

1. **Get the Pod URL**:
   - In Runpod console, find your pod
   - Click on "Connect" → "Connection Options"
   - Copy the HTTP Service URL (format: `https://[pod-id]-8501.proxy.runpod.net`)

2. **Access the Dashboard**:
   - Navigate to the URL in your browser
   - No login required - publicly accessible

## Public Access Configuration

### Important Considerations

Since this is a public dashboard with no authentication:

1. **Data Privacy**: Ensure search results don't contain sensitive information
2. **Access Monitoring**: Use Runpod logs to track usage
3. **Rate Limiting**: Consider implementing rate limits if needed
4. **HTTPS**: Always use HTTPS in production

### Optional Security Measures

Even for public dashboards, consider:
- Setting up HTTPS with SSL certificates
- Using a custom domain for professional appearance
- Implementing IP-based rate limiting
- Adding Cloudflare or similar CDN for DDoS protection

## Sharing the Dashboard

### Direct URL Access

1. Share the Runpod URL with anyone who needs access
2. No credentials required - publicly accessible
3. Suitable for public information sharing

Example sharing message:
```
Subject: VectorStock Dashboard Available

Hi Team,

Our VectorStock search dashboard is now publicly available at:
https://[your-pod-id]-8501.proxy.runpod.net

No login required - simply visit the URL to browse search results.
```

### Option 2: Custom Domain (Professional)

1. **Add a custom domain** in Runpod:
   - Go to pod settings → "Custom Domains"
   - Add your domain (e.g., `vectorstock.company.com`)
   - Update DNS CNAME record

2. **Configure SSL**:
   - Runpod provides automatic SSL certificates
   - Or use your own certificates

### Option 3: VPN Access (Most Secure)

1. Deploy the pod in a **private network**
2. Require VPN connection to access
3. Best for sensitive data or larger organizations

### Usage Guidelines

Since the dashboard is public:
- Anyone with the URL can view all search results
- Users can browse, filter, and search within results
- Consider what data is appropriate for public viewing

## Maintenance and Updates

### Updating the Dashboard

1. **Update local code**
2. **Rebuild Docker image**:
   ```bash
   docker build -t thebigpanda/vectorstock-dashboard:v2 .
   docker push thebigpanda/vectorstock-dashboard:v2
   ```
3. **Update Runpod pod**:
   - Stop the current pod
   - Update container image to new version
   - Restart pod

### Backing Up Data

1. **Download search results**:
   ```bash
   # SSH into pod
   ssh root@[pod-ip] -p [ssh-port]
   
   # Backup search results
   tar -czf backup-$(date +%Y%m%d).tar.gz /app/search_results
   ```

2. **Use Runpod volumes** for persistent storage

### Monitoring

- Check pod logs in Runpod console
- Monitor resource usage (CPU, RAM)
- Set up alerts for downtime

## Troubleshooting

### Common Issues

1. **"no matching manifest for linux/amd64" error**:
   - This occurs when building on Mac (ARM64) for Runpod (AMD64)
   - Solution: Use buildx for multi-platform builds:
     ```bash
     docker buildx build --platform linux/amd64 -t thebigpanda/vectorstock-dashboard:latest --push .
     ```
   - Or use the provided script: `./build-multiplatform.sh`

2. **"Connection refused" error**:
   - Check if pod is running
   - Verify port 8501 is exposed
   - Check firewall settings

2. **"Page not loading"**:
   - Verify the pod is running
   - Check if the URL is correct
   - Clear browser cache

3. **"Out of memory" errors**:
   - Increase pod RAM allocation
   - Reduce concurrent users
   - Optimize search result caching

4. **Slow performance**:
   - Upgrade to more vCPUs
   - Enable caching in Streamlit
   - Use spot instances during low-traffic hours

### Debug Mode

To debug issues, SSH into the pod:
```bash
# Get SSH credentials from Runpod console
ssh root@[pod-ip] -p [ssh-port]

# Check logs
docker logs $(docker ps -q)

# Test connectivity
curl http://localhost:8501
```

## Cost Optimization

1. **Use CPU pods** instead of GPU pods (no GPU needed)
2. **Deploy spot instances** for 50-80% cost savings
3. **Set auto-stop** after inactivity
4. **Scale down** during off-hours

Estimated costs:
- CPU Pod (4 vCPU, 8GB RAM): ~$0.08-0.12/hour
- Monthly cost (24/7): ~$60-90
- With spot instances: ~$30-45/month

## Support

For issues or questions:
1. Check Runpod documentation: https://docs.runpod.io
2. Review Streamlit deployment guides
3. Contact your IT administrator

---

## Quick Reference

**Access**: Public - no authentication required

**URLs**:
- Local test: http://localhost:8501
- Runpod: https://[pod-id]-8501.proxy.runpod.net

**Key Files**:
- `Dockerfile`: Container configuration
- `auth_config.py`: Authentication settings
- `docker-compose.yml`: Local testing
- `runpod-template.json`: Deployment template
