#!/usr/bin/env python3
"""
Test script to verify MongoDB connection status endpoints
"""
import asyncio
import httpx
import json
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

BASE_URL = "http://localhost:8000/api"

async def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n" + "="*60)
    print("Testing /health endpoint")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=10.0)
            data = response.json()
            print(f"Status Code: {response.status_code}")
            
            # Display main message
            message = data.get('message', 'No message')
            status = data.get('status', 'unknown')
            
            if status == 'healthy':
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
            
            print(f"\nFull Response:\n{json.dumps(data, indent=2)}")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_mongodb_status_endpoint():
    """Test the detailed MongoDB status endpoint"""
    print("\n" + "="*60)
    print("Testing /status/mongodb endpoint")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/status/mongodb", timeout=10.0)
            data = response.json()
            print(f"Status Code: {response.status_code}")
            
            # Display main message
            message = data.get('message', 'No message')
            status = data.get('status', 'unknown')
            
            if status == 'connected':
                print(f"✅ {message}")
            else:
                print(f"❌ {message}")
            
            print(f"\nFull Response:\n{json.dumps(data, indent=2)}")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_root_endpoint():
    """Test the root endpoint"""
    print("\n" + "="*60)
    print("Testing / endpoint")
    print("="*60)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/", timeout=10.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response:\n{json.dumps(response.json(), indent=2)}")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("\n🚀 Starting MongoDB Status Endpoint Tests")
    print(f"Base URL: {BASE_URL}")
    
    results = {
        "root": await test_root_endpoint(),
        "health": await test_health_endpoint(),
        "mongodb_status": await test_mongodb_status_endpoint(),
    }
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("✅ All tests passed!" if all_passed else "❌ Some tests failed"))
    
    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        exit(1)
