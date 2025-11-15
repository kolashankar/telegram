# Startup Log Reference - MongoDB Connection Status

## What You'll See in the Logs

When you start the backend server with `uvicorn server:app --host 0.0.0.0 --port 8001`, the MongoDB connection status will now be displayed at startup.

### When MongoDB is Connected Successfully

```
======================================================================
🔍 CHECKING MONGODB CONNECTION STATUS...
======================================================================
✅ MongoDB connected successfully
   Database: telegram_db
   Connection: Active
======================================================================
```

### When MongoDB Connection Fails

```
======================================================================
🔍 CHECKING MONGODB CONNECTION STATUS...
======================================================================
❌ Failed to connect MongoDB
   Error: Connection refused
   Database: telegram_db
======================================================================
```

## Full Startup Log Example

```
INFO:     Started server process [22882]
INFO:     Waiting for application startup.

======================================================================
🔍 CHECKING MONGODB CONNECTION STATUS...
======================================================================
✅ MongoDB connected successfully
   Database: telegram_db
   Connection: Active
======================================================================

2025-11-15 11:25:34,502 - server - INFO - 🤖 Starting Enhanced OTT Bot with Premium Features...
2025-11-15 11:25:34,502 - src.services.telegram.bot_enhanced - INFO - Enhanced OTT Bot initialized
2025-11-15 11:25:34,502 - server - INFO - ✅ Enhanced OTT Bot started successfully!
2025-11-15 11:25:34,502 - server - INFO -    - Premium Mode: True
2025-11-15 11:25:34,502 - server - INFO -    - Auto Approve: True
2025-11-15 11:25:34,502 - server - INFO -    - Force Subscribe: Enabled
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

## Key Points

- **Timing**: MongoDB status is checked at the very beginning of server startup
- **Visibility**: The status is clearly marked with ✅ (success) or ❌ (failure)
- **Details**: Shows database name and connection status
- **Error Info**: If connection fails, the error message is displayed
- **Order**: MongoDB check happens before the Telegram bot initialization

## API Endpoints for Status

You can also check MongoDB status at any time using these endpoints:

### 1. Quick Health Check
```bash
curl http://localhost:8001/api/health
```

### 2. Detailed Status
```bash
curl http://localhost:8001/api/status/mongodb
```

## Testing

To test the startup logs:

1. Start the server:
   ```bash
   source venv/bin/activate
   uvicorn server:app --host 0.0.0.0 --port 8001
   ```

2. Look for the MongoDB connection status in the logs at startup

3. If MongoDB is connected, you'll see: `✅ MongoDB connected successfully`

4. If MongoDB is not connected, you'll see: `❌ Failed to connect MongoDB`
