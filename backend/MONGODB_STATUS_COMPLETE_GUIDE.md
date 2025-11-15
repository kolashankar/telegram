# MongoDB Connection Status - Complete Implementation Guide

## Overview

The backend has been enhanced with comprehensive MongoDB connection status monitoring. The status is now displayed:

1. **In startup logs** - When the server starts
2. **Via REST API endpoints** - On demand
3. **Via monitoring dashboard** - Real-time tracking

---

## 1. Startup Logs

### What You'll See

When you start the server:
```bash
uvicorn server:app --host 0.0.0.0 --port 8001
```

You'll see MongoDB status in the logs:

**Success:**
```
======================================================================
🔍 CHECKING MONGODB CONNECTION STATUS...
======================================================================
✅ MongoDB connected successfully
   Database: telegram_db
   Connection: Active
======================================================================
```

**Failure:**
```
======================================================================
🔍 CHECKING MONGODB CONNECTION STATUS...
======================================================================
❌ Failed to connect MongoDB
   Error: Connection refused
   Database: telegram_db
======================================================================
```

### Implementation

Location: `server.py` - `startup_event()` function (lines 844-863)

The check happens automatically when the server starts, before the Telegram bot initialization.

---

## 2. REST API Endpoints

### Endpoint 1: Quick Health Check

**URL:** `GET /api/health`

**Purpose:** Fast connectivity verification

**Response (Connected):**
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

**Response (Disconnected):**
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

**Test with cURL:**
```bash
curl http://localhost:8001/api/health
```

---

### Endpoint 2: Detailed Status

**URL:** `GET /api/status/mongodb`

**Purpose:** Comprehensive database monitoring

**Response (Connected):**
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

**Response (Disconnected):**
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

**Test with cURL:**
```bash
curl http://localhost:8001/api/status/mongodb
```

---

## 3. Monitoring Tools

### Test Script

**File:** `test_mongodb_status.py`

Tests all endpoints and displays results:

```bash
python test_mongodb_status.py
```

**Output:**
```
🚀 Starting MongoDB Status Endpoint Tests
Base URL: http://localhost:8000/api

============================================================
Testing / endpoint
============================================================
Status Code: 200
Response:
{
  "message": "Telegram DRM Bot API",
  "version": "1.0.0"
}

============================================================
Testing /health endpoint
============================================================
Status Code: 200
✅ MONGODB CONNECTED SUCCESSFULLY

Full Response:
{
  "status": "healthy",
  "message": "MongoDB connected successfully",
  ...
}

============================================================
Testing /status/mongodb endpoint
============================================================
Status Code: 200
✅ MONGODB CONNECTED SUCCESSFULLY

Full Response:
{
  "status": "connected",
  "message": "MongoDB connected successfully",
  ...
}

============================================================
Test Summary
============================================================
root: ✅ PASSED
health: ✅ PASSED
mongodb_status: ✅ PASSED

✅ All tests passed!
```

---

### Monitoring Dashboard

**File:** `monitor_mongodb.py`

Real-time monitoring with beautiful formatted output:

**Single Check:**
```bash
python monitor_mongodb.py
```

**Continuous Monitoring (updates every 30 seconds):**
```bash
python monitor_mongodb.py --continuous
```

**Custom Interval (every 60 seconds):**
```bash
python monitor_mongodb.py --continuous --interval 60
```

**Custom API URL:**
```bash
python monitor_mongodb.py --url http://api.example.com/api --continuous
```

**Output Example:**
```
🚀 Starting MongoDB Monitor
📍 Base URL: http://localhost:8001/api
⏱️  Update Interval: 30 seconds
Press Ctrl+C to stop

[Iteration 1] 2025-11-15 11:22:00

======================================================================
  MONGODB CONNECTION HEALTH CHECK
======================================================================

✅ MONGODB CONNECTED SUCCESSFULLY

Status: HEALTHY
Database: telegram_db
Timestamp: 2024-11-15T11:22:00.000000+00:00

======================================================================
  DETAILED MONGODB STATUS
======================================================================

✅ MONGODB CONNECTED SUCCESSFULLY

📊 Connection Information
----------------------------------------------------------------------
Status: ACTIVE
Database: telegram_db
URL: mongodb+srv://***@cluster0.cqrny5c.mongodb.net/***

📊 Server Information
----------------------------------------------------------------------
Uptime: 1.00 hours (3600 seconds)
Connections:
  • Current: 5
  • Available: 995
  • Total Created: 10
Network:
  • Bytes In: 1000.00 KB
  • Bytes Out: 500.00 KB
  • Requests: 150

📊 Database Statistics
----------------------------------------------------------------------
Size: 5.00 MB
Storage Allocated: 8.00 MB
Collections: 8
Indexes: 12
Average Document Size: 1024 bytes

Collections (8):
  1. users
  2. extractions
  3. payments
  4. user_configs
  5. admins
  6. user_usage
  7. broadcasts
  8. downloads

📊 Health Status
----------------------------------------------------------------------
✅ Is Master: True
✅ Server OK: True

Timestamp: 2024-11-15T11:22:00.000000+00:00

⏳ Next check in 30 seconds...
```

---

## Files Modified/Created

### Modified Files

1. **server.py**
   - Added `/api/health` endpoint (lines 102-126)
   - Added `/api/status/mongodb` endpoint (lines 128-190)
   - Added MongoDB status check in startup event (lines 848-863)

### New Files Created

1. **test_mongodb_status.py** - Automated test script
2. **monitor_mongodb.py** - Real-time monitoring dashboard
3. **MONGODB_STATUS_GUIDE.md** - Comprehensive documentation
4. **QUICK_START_MONGODB_STATUS.md** - Quick reference
5. **STARTUP_LOG_REFERENCE.md** - Startup log examples
6. **MONGODB_STATUS_COMPLETE_GUIDE.md** - This file

---

## Quick Reference

| Feature | Location | Command |
|---------|----------|---------|
| Startup Logs | Server logs | `uvicorn server:app --host 0.0.0.0 --port 8001` |
| Health Check API | `/api/health` | `curl http://localhost:8001/api/health` |
| Detailed Status API | `/api/status/mongodb` | `curl http://localhost:8001/api/status/mongodb` |
| Test Script | `test_mongodb_status.py` | `python test_mongodb_status.py` |
| Monitor Dashboard | `monitor_mongodb.py` | `python monitor_mongodb.py --continuous` |

---

## Key Messages

- **Success:** `✅ MongoDB connected successfully`
- **Failure:** `❌ Failed to connect MongoDB`

These messages appear in:
- Startup logs
- API responses
- Monitoring dashboard
- Test output

---

## Troubleshooting

### MongoDB Not Connecting

1. Check `.env` file for correct `MONGO_URL`
2. Verify MongoDB server is running
3. Check network connectivity
4. Verify credentials in connection string
5. Check firewall rules

### Endpoints Not Responding

1. Ensure server is running: `uvicorn server:app --host 0.0.0.0 --port 8001`
2. Check port 8001 is not in use
3. Verify API URL is correct
4. Check for firewall blocking

### Logs Not Showing

1. Ensure logging is configured in server.py
2. Check console output (not redirected)
3. Verify log level is INFO or DEBUG

---

## Integration Examples

### Python Integration

```python
import httpx
import asyncio

async def check_mongodb():
    async with httpx.AsyncClient() as client:
        # Health check
        response = await client.get("http://localhost:8001/api/health")
        data = response.json()
        
        if data['status'] == 'healthy':
            print(f"✅ {data['message']}")
        else:
            print(f"❌ {data['message']}")

asyncio.run(check_mongodb())
```

### JavaScript/Node.js Integration

```javascript
async function checkMongoDB() {
  try {
    const response = await fetch('http://localhost:8001/api/health');
    const data = await response.json();
    
    if (data.status === 'healthy') {
      console.log(`✅ ${data.message}`);
    } else {
      console.log(`❌ ${data.message}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

checkMongoDB();
```

---

## Summary

MongoDB connection status is now monitored and displayed in three ways:

1. **Startup Logs** - Automatic check when server starts
2. **REST APIs** - On-demand status checks via HTTP
3. **Monitoring Tools** - Real-time dashboard and testing scripts

All display clear messages: **"MongoDB connected successfully"** or **"Failed to connect MongoDB"**
