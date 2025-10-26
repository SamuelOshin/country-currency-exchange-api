# Leapcell Deployment Instructions

## Problem Solved
The `/refresh` endpoint was failing in production with error:
```
[Errno 30] Read-only file system: '/app/app/cache/summary.png'
```

This was caused by Leapcell's read-only file system. The solution implemented uses `/tmp/cache` in production.

## Required Environment Variables in Leapcell

Set these environment variables in your Leapcell project settings:

```env
# Database Configuration
DATABASE_URL=input here

# SSL Configuration
SSL_CERT_PATH=ca.pem
SSL_VERIFY=True

# Server Configuration
HOST=0.0.0.0
PORT=8000

# External APIs
RESTCOUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_API_URL=https://open.er-api.com/v6/latest/USD

# API Configuration
API_TIMEOUT=30
CACHE_DIR=/tmp/cache

# Environment - CRITICAL: Must be "production" for Leapcell
ENVIRONMENT=production
```

## Key Changes Made

### 1. Config.py - Smart Cache Path Selection
- Development: Uses `app/cache` (local directory)
- Production: Uses `/tmp/cache` (writable in containers)
- Automatic fallback if primary cache directory fails

### 2. Image Service - Robust Directory Creation
- Creates cache directory before saving image
- Has fallback to `/tmp/cache` if primary fails
- Checks both locations when retrieving image
- Added comprehensive logging

### 3. External API Service - Enhanced Error Handling
- Explicit SSL verification (`verify=True`)
- Follow redirects enabled
- Detailed error logging with different error types
- Better exception messages

## Testing

### Local Testing
```bash
# Run locally (uses app/cache)
uvicorn app.main:app --reload

# Test refresh endpoint
curl -X POST http://localhost:8000/api/v1/countries/refresh

# Check image endpoint
curl http://localhost:8000/api/v1/countries/image
```

### Production Testing (Leapcell)
```bash
# Test refresh endpoint
curl -X POST https://your-app.leapcell.dev/api/v1/countries/refresh

# Check image endpoint
curl https://your-app.leapcell.dev/api/v1/countries/image

# Check logs
# Go to Leapcell dashboard → Logs
# Look for:
# - "Creating cache directory: /tmp/cache"
# - "Saving summary image to: /tmp/cache/summary.png"
# - "Successfully saved summary image"
```

## How It Works

1. **Development Mode** (`ENVIRONMENT=development`):
   - Uses `app/cache` directory relative to project
   - Works on local machines with writable file systems

2. **Production Mode** (`ENVIRONMENT=production`):
   - Automatically uses `/tmp/cache` 
   - `/tmp` is writable even in read-only containers
   - Images persist during container lifetime (cleared on restart)

3. **Image Retrieval**:
   - `get_image_path()` checks both locations
   - Returns first found image
   - Ensures compatibility across environments

## Important Notes

⚠️ **Image Persistence**: Images in `/tmp/cache` are **ephemeral** - they're cleared when the container restarts. This is fine because:
- The `/refresh` endpoint regenerates the image
- Images are meant to be fresh snapshots
- First request after restart will regenerate the image

✅ **SSL Certificate**: The SSL certificate (`ca.pem`) should be included in your deployment or uploaded separately to Leapcell.

📊 **Monitoring**: Check Leapcell logs regularly to ensure:
- External APIs are responding (HTTP 200 OK)
- Cache directory is created successfully
- Images are being saved and served

## Troubleshooting

### If refresh still fails:
1. Check Leapcell logs for specific error
2. Verify `ENVIRONMENT=production` is set
3. Ensure `/tmp` is writable (should be by default)

### If image endpoint returns 404:
1. Run `/refresh` endpoint first
2. Check logs for "Successfully saved summary image"
3. Verify image exists: `ls /tmp/cache/summary.png` (via Leapcell shell if available)

### External API issues:
- Logs will show specific API that failed
- Check if Leapcell blocks outbound HTTPS
- Verify API URLs are correct in env vars
