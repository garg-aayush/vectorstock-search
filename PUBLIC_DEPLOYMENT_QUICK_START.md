# VectorStock Dashboard - Public Deployment Quick Start

Deploy your VectorStock dashboard as a public endpoint on Runpod in minutes!

## 🚀 Quick Deployment (5 minutes)

### 1. Build & Push Docker Image

```bash
# Set your Docker Hub username
export DOCKER_USERNAME="thebigpanda"

# Build the image for linux/amd64 (required for Runpod)
# Use buildx for multi-platform support
docker buildx build --platform linux/amd64 -t $DOCKER_USERNAME/vectorstock-dashboard:latest --push .

# Alternative: Use the provided script
./build-multiplatform.sh
```

### 2. Deploy on Runpod

1. Go to [runpod.io](https://runpod.io) → Console
2. Click **"Deploy"** → **"CPU Pod"** (no GPU needed)
3. Configure:
   - **Container Image**: `thebigpanda/vectorstock-dashboard:latest`
   - **Exposed HTTP Ports**: `8501`
   - **Disk**: 10 GB
   - **vCPU**: 2-4 cores
   - **RAM**: 4-8 GB

4. Click **"Deploy"**

### 3. Access Your Dashboard

- Get URL from Runpod: `https://[pod-id]-8501.proxy.runpod.net`
- Share with anyone - no login required!
- Dashboard is publicly accessible

## 💰 Cost Estimate

- **CPU Pod**: ~$0.08-0.12/hour
- **Monthly (24/7)**: ~$60-90
- **With Spot Instances**: ~$30-45/month

## 🎯 What You Get

- ✅ Public web dashboard
- ✅ Browse all VectorStock search results  
- ✅ Filter by license, artist, credits
- ✅ Search within results
- ✅ View detailed image information
- ✅ Accessible from any device/browser

## 📝 Notes

- This is a **public endpoint** - anyone with the URL can access
- Ensure your search results don't contain sensitive data
- Consider using a custom domain for professional appearance

## 🆘 Troubleshooting

**Dashboard not loading?**
- Check pod is running in Runpod console
- Verify port 8501 is exposed
- Try refreshing after 2-3 minutes

**Need help?**
- Check Runpod logs
- Ensure Docker image uploaded successfully
- Verify search_results folder has data

---

That's it! Your dashboard should be live in under 5 minutes. 🎉
