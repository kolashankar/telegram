# MongoDB Connection Status Endpoints

This guide documents the new MongoDB connection status endpoints added to the backend API.

## Overview

The backend now provides two endpoints to monitor MongoDB connection status:

1. **`/api/health`** - Quick health check
2. **`/api/status/mongodb`** - Detailed MongoDB status information

## Endpoints

### 1. Health Check Endpoint

**URL:** `GET /api/health`

**Description:** Quick health check that verifies the API and MongoDB connection status.

**Response (Success):**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-15T11:19:00.000000+00:00",
  "mongodb": {
    "status": "connected",
    "error": null,
    "database": "telegram_db"
  }
}
```

**Response (Failure):**
```json
{
  "status": "unhealthy",
  "timestamp": "2024-11-15T11:19:00.000000+00:00",
  "mongodb": {
    "status": "disconnected",
    "error": "Connection refused",
    "database": "telegram_db"
  }
}
```

**Use Cases:**
- Quick monitoring/alerting
- Load balancer health checks
- Uptime monitoring services
- Simple connectivity verification

---

### 2. Detailed MongoDB Status Endpoint

**URL:** `GET /api/status/mongodb`

**Description:** Comprehensive MongoDB connection and database statistics.

**Response (Success):**
```json
{
  "status": "connected",
  "timestamp": "2024-11-15T11:19:00.000000+00:00",
  "connection": {
    "url": "mongodb+srv://***@cluster0.cqrny5c.mongodb.net/***",
    "database": "telegram_db",
    "status": "active"
  },
  "server": {
    "uptime_seconds": 3600,
    "connections": {
      "current": 5,
      "available": 995,
      "totalCreated": 10
    },
    "network": {
      "bytesIn": 1024000,
      "bytesOut": 512000,
      "numRequests": 150
    }
  },
  "database": {
    "size_bytes": 5242880,
    "storage_size_bytes": 8388608,
    "collections_count": 8,
    "collections": [
      "users",
      "extractions",
      "payments",
      "user_configs",
      "admins",
      "user_usage",
      "broadcasts",
      "downloads"
    ],
    "indexes": 12,
    "avg_obj_size": 1024
  },
  "health": {
    "is_master": true,
    "ok": true
  }
}
```

**Response (Failure):**
```json
{
  "status": "disconnected",
  "timestamp": "2024-11-15T11:19:00.000000+00:00",
  "error": "Connection timeout",
  "connection": {
    "url": "***",
    "database": "telegram_db",
    "status": "inactive"
  }
}
```

**Use Cases:**
- Detailed monitoring dashboards
- Database performance analysis
- Capacity planning
- Troubleshooting connection issues
- Collection and index statistics

---

## Response Fields Explained

### Connection Object
- **url**: MongoDB connection URL (credentials masked for security)
- **database**: Database name
- **status**: Connection status ("active" or "inactive")

### Server Object
- **uptime_seconds**: MongoDB server uptime in seconds
- **connections**: Connection pool statistics
  - `current`: Currently active connections
  - `available`: Available connections in pool
  - `totalCreated`: Total connections created since startup
- **network**: Network statistics
  - `bytesIn`: Total bytes received
  - `bytesOut`: Total bytes sent
  - `numRequests`: Total number of requests

### Database Object
- **size_bytes**: Actual data size in bytes
- **storage_size_bytes**: Allocated storage size in bytes
- **collections_count**: Number of collections
- **collections**: List of all collection names
- **indexes**: Total number of indexes
- **avg_obj_size**: Average document size in bytes

### Health Object
- **is_master**: Whether this is the primary node (for replica sets)
- **ok**: Server status (1 = OK, 0 = error)

---

## Testing the Endpoints

### Using cURL

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test detailed status endpoint
curl http://localhost:8000/api/status/mongodb
```

### Using Python

```python
import httpx
import asyncio

async def check_status():
    async with httpx.AsyncClient() as client:
        # Health check
        health = await client.get("http://localhost:8000/api/health")
        print(health.json())
        
        # Detailed status
        status = await client.get("http://localhost:8000/api/status/mongodb")
        print(status.json())

asyncio.run(check_status())
```

### Using the Test Script

```bash
# Run the provided test script
python test_mongodb_status.py
```

---

## Integration Examples

### 1. Monitoring Dashboard

```python
import httpx
import time
from datetime import datetime

async def monitor_mongodb():
    """Continuously monitor MongoDB status"""
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get("http://localhost:8000/api/status/mongodb")
                data = response.json()
                
                if data['status'] == 'connected':
                    print(f"✅ MongoDB Connected")
                    print(f"   Collections: {data['database']['collections_count']}")
                    print(f"   Size: {data['database']['size_bytes'] / 1024 / 1024:.2f} MB")
                    print(f"   Active Connections: {data['server']['connections']['current']}")
                else:
                    print(f"❌ MongoDB Disconnected: {data.get('error')}")
            except Exception as e:
                print(f"❌ Error: {e}")
            
            time.sleep(30)  # Check every 30 seconds
```

### 2. Alerting System

```python
import httpx
import smtplib

async def alert_on_failure():
    """Send alert if MongoDB connection fails"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/health")
        data = response.json()
        
        if data['status'] == 'unhealthy':
            # Send email alert
            send_alert_email(
                subject="MongoDB Connection Failed",
                message=f"Error: {data['mongodb']['error']}"
            )
```

### 3. Capacity Planning

```python
async def analyze_capacity():
    """Analyze database capacity for planning"""
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/status/mongodb")
        data = response.json()
        
        db_info = data['database']
        size_mb = db_info['size_bytes'] / 1024 / 1024
        storage_mb = db_info['storage_size_bytes'] / 1024 / 1024
        
        print(f"Database Size: {size_mb:.2f} MB")
        print(f"Storage Allocated: {storage_mb:.2f} MB")
        print(f"Utilization: {(size_mb/storage_mb)*100:.1f}%")
        print(f"Collections: {db_info['collections_count']}")
        print(f"Average Document Size: {db_info['avg_obj_size']} bytes")
```

---

## Error Handling

Both endpoints handle errors gracefully:

- **Connection Timeout**: Returns status "disconnected" with timeout error
- **Authentication Failure**: Returns status "disconnected" with auth error
- **Network Error**: Returns status "disconnected" with network error
- **Invalid Database**: Returns status "disconnected" with database error

All errors are logged for debugging purposes.

---

## Security Considerations

1. **Credentials Masked**: MongoDB connection URLs have credentials masked as `***`
2. **No Sensitive Data**: Endpoints don't expose sensitive configuration
3. **Error Messages**: Error messages are generic to avoid information leakage
4. **Rate Limiting**: Consider adding rate limiting for production use

---

## Performance Notes

- **Health Check**: ~10-50ms (minimal overhead)
- **Detailed Status**: ~50-200ms (includes server stats)
- **No Database Queries**: Status endpoints don't query collections
- **Async**: Both endpoints are fully async for non-blocking operation

---

## Troubleshooting

### MongoDB Connection Fails

1. Check MongoDB URL in `.env` file
2. Verify network connectivity to MongoDB server
3. Check MongoDB credentials
4. Verify firewall rules allow connection
5. Check MongoDB server status

### Slow Response Times

1. Check network latency to MongoDB
2. Verify MongoDB server performance
3. Check for connection pool exhaustion
4. Monitor server resources (CPU, memory, disk)

### Collections Not Showing

1. Ensure collections exist in the database
2. Check database name in `.env`
3. Verify user has read permissions

---

## API Reference Summary

| Endpoint | Method | Purpose | Response Time |
|----------|--------|---------|----------------|
| `/api/health` | GET | Quick health check | ~10-50ms |
| `/api/status/mongodb` | GET | Detailed status | ~50-200ms |
| `/api/` | GET | API info | ~1ms |

---

## Future Enhancements

- [ ] Add metrics export (Prometheus format)
- [ ] Add historical data tracking
- [ ] Add performance benchmarking
- [ ] Add automatic alerting
- [ ] Add backup status monitoring
- [ ] Add replication status monitoring
