# Quick Start - MongoDB Connection Status

## Overview

Two simple endpoints to check MongoDB connection status:

### 1. Quick Health Check: `/api/health`

**When MongoDB is Connected:**
```json
{
  "status": "healthy",
  "message": "MongoDB connected successfully",
  "timestamp": "2024-11-15T11:22:00.000000+00:00",
  "mongodb": {
    "status": "connected",
    "message": "MongoDB connected successfully",
    "error": null,
    "database": "telegram_db"
  }
}
```

**When MongoDB is Disconnected:**
```json
{
  "status": "unhealthy",
  "message": "Failed to connect MongoDB",
  "timestamp": "2024-11-15T11:22:00.000000+00:00",
  "mongodb": {
    "status": "disconnected",
    "message": "Failed to connect MongoDB",
    "error": "Connection refused",
    "database": "telegram_db"
  }
}
```

---

### 2. Detailed Status: `/api/status/mongodb`

**When MongoDB is Connected:**
```json
{
  "status": "connected",
  "message": "MongoDB connected successfully",
  "timestamp": "2024-11-15T11:22:00.000000+00:00",
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
    "collections": ["users", "extractions", "payments", "user_configs", "admins", "user_usage", "broadcasts", "downloads"],
    "indexes": 12,
    "avg_obj_size": 1024
  },
  "health": {
    "is_master": true,
    "ok": true
  }
}
```

**When MongoDB is Disconnected:**
```json
{
  "status": "disconnected",
  "message": "Failed to connect MongoDB",
  "timestamp": "2024-11-15T11:22:00.000000+00:00",
  "error": "Connection timeout",
  "connection": {
    "url": "***",
    "database": "telegram_db",
    "status": "inactive"
  }
}
```

---

## Testing

### Using cURL

```bash
# Quick health check
curl http://localhost:8000/api/health

# Detailed status
curl http://localhost:8000/api/status/mongodb
```

### Using Python

```python
import httpx
import asyncio

async def check():
    async with httpx.AsyncClient() as client:
        # Health check
        resp = await client.get("http://localhost:8000/api/health")
        print(resp.json())

asyncio.run(check())
```

### Using Test Script

```bash
python test_mongodb_status.py
```

### Using Monitor Script

```bash
# Single check
python monitor_mongodb.py

# Continuous monitoring
python monitor_mongodb.py --continuous
```

---

## Key Messages

| Scenario | Message |
|----------|---------|
| ✅ Connected | **"MongoDB connected successfully"** |
| ❌ Disconnected | **"Failed to connect MongoDB"** |

---

## Files Created

1. **server.py** - Updated with two new endpoints
2. **test_mongodb_status.py** - Test script to verify endpoints
3. **monitor_mongodb.py** - Real-time monitoring dashboard
4. **MONGODB_STATUS_GUIDE.md** - Comprehensive documentation
5. **QUICK_START_MONGODB_STATUS.md** - This file

---

## Next Steps

1. Start the backend server:
   ```bash
   python server.py
   ```

2. In another terminal, test the endpoints:
   ```bash
   python test_mongodb_status.py
   ```

3. Or use the monitor for continuous tracking:
   ```bash
   python monitor_mongodb.py --continuous
   ```
