# Background Tasks Guide

## Overview

The `/countries/refresh` endpoint runs as a background task to prevent timeouts on platforms with request time limits (e.g., Leapcell has a 360-second/6-minute timeout).

## How It Works

### Starting a Refresh

**Endpoint:** `POST /api/v1/countries/refresh`

**Response (Immediate):**
```json
{
  "message": "Country refresh started in background",
  "status": "started",
  "started_at": "2024-01-15T10:30:00"
}
```

If a refresh is already running:
```json
{
  "message": "Refresh already in progress",
  "status": "already_running",
  "started_at": "2024-01-15T10:29:00"
}
```

### Checking Status

**Endpoint:** `GET /api/v1/countries/refresh/status`

**Response (Running):**
```json
{
  "is_running": true,
  "status": "running",
  "started_at": "2024-01-15T10:30:00",
  "completed_at": null,
  "countries_processed": 0,
  "error": null
}
```

**Response (Completed):**
```json
{
  "is_running": false,
  "status": "completed",
  "started_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:35:00",
  "countries_processed": 250,
  "error": null
}
```

**Response (Error):**
```json
{
  "is_running": false,
  "status": "error",
  "started_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:32:00",
  "countries_processed": 50,
  "error": "Failed to fetch data from external API"
}
```

## Usage Examples

### Using cURL

```bash
# Start refresh
curl -X POST https://your-app.leapcell.dev/api/v1/countries/refresh

# Check status
curl https://your-app.leapcell.dev/api/v1/countries/refresh/status
```

### Using Python

```python
import requests
import time

# Start refresh
response = requests.post("https://your-app.leapcell.dev/api/v1/countries/refresh")
print(response.json())

# Poll status until complete
while True:
    status = requests.get("https://your-app.leapcell.dev/api/v1/countries/refresh/status")
    data = status.json()
    
    if not data["is_running"]:
        print(f"Refresh complete! Processed {data['countries_processed']} countries")
        break
    
    print(f"Still running... {data['countries_processed']} countries processed so far")
    time.sleep(5)  # Check every 5 seconds
```

### Using JavaScript/Fetch

```javascript
// Start refresh
fetch('https://your-app.leapcell.dev/api/v1/countries/refresh', {
  method: 'POST'
})
  .then(res => res.json())
  .then(data => console.log(data));

// Poll status
async function checkRefreshStatus() {
  while (true) {
    const response = await fetch('https://your-app.leapcell.dev/api/v1/countries/refresh/status');
    const data = await response.json();
    
    if (!data.is_running) {
      console.log(`Refresh complete! Processed ${data.countries_processed} countries`);
      break;
    }
    
    console.log(`Still running... ${data.countries_processed} countries processed`);
    await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
  }
}

checkRefreshStatus();
```

## Performance Optimizations

The background task includes several optimizations:

1. **Connection Pooling**: Database maintains a pool of 10 connections with up to 20 overflow connections
2. **Batch Processing**: Countries are processed and committed in batches of 50 to reduce database overhead
3. **Async Processing**: The task runs in the background, freeing up the web server to handle other requests
4. **Status Tracking**: Global state tracking allows monitoring without blocking the main thread

## Expected Performance

- **Response Time**: POST /countries/refresh responds in <1 second
- **Processing Time**: Full refresh of 250+ countries takes approximately 3-5 minutes
- **Database Commits**: Occurs every 50 countries (5 batches total for 250 countries)

## Monitoring

Monitor the refresh process by:

1. Checking the status endpoint periodically
2. Watching application logs for progress updates
3. Verifying `countries_processed` count increases over time

## Troubleshooting

### Refresh Never Completes

Check application logs for errors. Common issues:
- External API (restcountries.com or open.er-api.com) is down
- Database connection issues
- Memory constraints on the server

### Status Shows "already_running" Forever

The `is_running` flag may be stuck. Restart the application to reset the state.

### Slow Performance

If refresh takes longer than expected:
- Check database connection latency
- Verify external API response times
- Monitor server CPU and memory usage

## Best Practices

1. **Don't Poll Too Frequently**: Check status every 5-10 seconds, not every second
2. **Handle Errors**: Always check for the `error` field in the status response
3. **Set Timeouts**: When polling, set a maximum wait time (e.g., 10 minutes)
4. **Log Completion**: Record when refreshes complete for monitoring purposes

## Architecture Notes

The background task pattern solves the platform timeout issue:

- **Before**: Synchronous processing → 6+ minute response time → timeout on Leapcell
- **After**: Immediate response + background processing → <1 second response → no timeout

This allows deployment on platforms with strict timeout limits while still processing large datasets.
