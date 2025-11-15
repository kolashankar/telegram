#!/usr/bin/env python3
"""
MongoDB Connection Status Monitor
Real-time monitoring dashboard for MongoDB connection status
"""
import asyncio
import httpx
import json
from datetime import datetime
from typing import Dict, Optional
import sys

class MongoDBMonitor:
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.health_url = f"{base_url}/health"
        self.status_url = f"{base_url}/status/mongodb"
        self.last_status = None
        self.error_count = 0
        self.success_count = 0
    
    async def fetch_health(self) -> Optional[Dict]:
        """Fetch health status"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.health_url)
                return response.json()
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    async def fetch_detailed_status(self) -> Optional[Dict]:
        """Fetch detailed MongoDB status"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.status_url)
                return response.json()
        except Exception as e:
            return {"error": str(e), "status": "error"}
    
    def format_bytes(self, bytes_val: int) -> str:
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_val < 1024:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.2f} TB"
    
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_section(self, title: str):
        """Print formatted section"""
        print(f"\n📊 {title}")
        print("-" * 70)
    
    async def display_health(self):
        """Display health status"""
        self.print_header("MONGODB CONNECTION HEALTH CHECK")
        
        health = await self.fetch_health()
        
        if "error" in health:
            print(f"❌ Error: {health['error']}")
            self.error_count += 1
            return
        
        status = health.get('status', 'unknown')
        message = health.get('message', 'No message')
        mongo_status = health.get('mongodb', {})
        
        # Display main message prominently
        status_icon = "✅" if status == "healthy" else "❌"
        print(f"\n{status_icon} {message.upper()}\n")
        
        # Additional details
        print(f"Status: {status.upper()}")
        print(f"Database: {mongo_status.get('database', 'N/A')}")
        
        if mongo_status.get('error'):
            print(f"Error Details: {mongo_status['error']}")
        
        print(f"Timestamp: {health.get('timestamp', 'N/A')}")
        
        self.success_count += 1
    
    async def display_detailed_status(self):
        """Display detailed MongoDB status"""
        self.print_header("DETAILED MONGODB STATUS")
        
        status = await self.fetch_detailed_status()
        
        if "error" in status:
            print(f"❌ Error: {status['error']}")
            self.error_count += 1
            return
        
        # Display main message prominently
        message = status.get('message', 'No message')
        status_value = status.get('status', 'unknown')
        status_icon = "✅" if status_value == "connected" else "❌"
        print(f"\n{status_icon} {message.upper()}\n")
        
        # Connection Info
        self.print_section("Connection Information")
        conn = status.get('connection', {})
        print(f"Status: {conn.get('status', 'N/A').upper()}")
        print(f"Database: {conn.get('database', 'N/A')}")
        print(f"URL: {conn.get('url', 'N/A')}")
        
        # Server Info
        self.print_section("Server Information")
        server = status.get('server', {})
        uptime_hours = server.get('uptime_seconds', 0) / 3600
        print(f"Uptime: {uptime_hours:.2f} hours ({server.get('uptime_seconds', 0)} seconds)")
        
        connections = server.get('connections', {})
        print(f"Connections:")
        print(f"  • Current: {connections.get('current', 'N/A')}")
        print(f"  • Available: {connections.get('available', 'N/A')}")
        print(f"  • Total Created: {connections.get('totalCreated', 'N/A')}")
        
        network = server.get('network', {})
        print(f"Network:")
        print(f"  • Bytes In: {self.format_bytes(network.get('bytesIn', 0))}")
        print(f"  • Bytes Out: {self.format_bytes(network.get('bytesOut', 0))}")
        print(f"  • Requests: {network.get('numRequests', 'N/A')}")
        
        # Database Info
        self.print_section("Database Statistics")
        db = status.get('database', {})
        print(f"Size: {self.format_bytes(db.get('size_bytes', 0))}")
        print(f"Storage Allocated: {self.format_bytes(db.get('storage_size_bytes', 0))}")
        print(f"Collections: {db.get('collections_count', 'N/A')}")
        print(f"Indexes: {db.get('indexes', 'N/A')}")
        print(f"Average Document Size: {db.get('avg_obj_size', 'N/A')} bytes")
        
        # Collections List
        collections = db.get('collections', [])
        if collections:
            print(f"\nCollections ({len(collections)}):")
            for i, col in enumerate(collections, 1):
                print(f"  {i}. {col}")
        
        # Health Info
        self.print_section("Health Status")
        health = status.get('health', {})
        is_master = health.get('is_master', False)
        is_ok = health.get('ok', False)
        
        master_icon = "✅" if is_master else "⚠️"
        ok_icon = "✅" if is_ok else "❌"
        
        print(f"{master_icon} Is Master: {is_master}")
        print(f"{ok_icon} Server OK: {is_ok}")
        
        print(f"\nTimestamp: {status.get('timestamp', 'N/A')}")
        
        self.success_count += 1
    
    async def continuous_monitor(self, interval: int = 30):
        """Continuously monitor MongoDB status"""
        print("\n🚀 Starting MongoDB Monitor")
        print(f"📍 Base URL: {self.base_url}")
        print(f"⏱️  Update Interval: {interval} seconds")
        print("Press Ctrl+C to stop\n")
        
        try:
            iteration = 0
            while True:
                iteration += 1
                print(f"\n[Iteration {iteration}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                await self.display_health()
                await self.display_detailed_status()
                
                print(f"\n⏳ Next check in {interval} seconds...")
                await asyncio.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\n⛔ Monitor stopped by user")
            self.print_summary()
    
    def print_summary(self):
        """Print monitoring summary"""
        self.print_header("MONITORING SUMMARY")
        print(f"✅ Successful Checks: {self.success_count}")
        print(f"❌ Failed Checks: {self.error_count}")
        total = self.success_count + self.error_count
        if total > 0:
            success_rate = (self.success_count / total) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")
    
    async def single_check(self):
        """Perform a single status check"""
        await self.display_health()
        await self.display_detailed_status()
        self.print_summary()

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MongoDB Connection Status Monitor"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000/api",
        help="Base API URL (default: http://localhost:8000/api)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Monitor update interval in seconds (default: 30)"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run continuous monitoring (default: single check)"
    )
    
    args = parser.parse_args()
    
    monitor = MongoDBMonitor(base_url=args.url)
    
    if args.continuous:
        await monitor.continuous_monitor(interval=args.interval)
    else:
        await monitor.single_check()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⛔ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
