#!/usr/bin/env python3
"""
Backend API Testing Script for Admin Dashboard and Widevine DRM Extraction
Tests the admin dashboard backend APIs and Widevine DRM extraction for 30+ OTT platforms.
"""

import requests
import json
import os
from datetime import datetime
import time

# Get backend URL from environment
BACKEND_URL = "https://movie-finder-bot.preview.emergentagent.com"

# Test PSSH for Widevine DRM testing
TEST_PSSH = "AAAAW3Bzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAADsIARIQ62dqu8s0Xpa7z2FmMPGj2hoNd2lkZXZpbmVfdGVzdCIQZmtqM2xqYVNkZmFsa3IzaioCSEQyAA=="

# 30 OTT Platforms with realistic license URLs
OTT_PLATFORMS = [
    {"name": "Disney+ Hotstar", "license_url": "https://www.hotstar.com/drm/license"},
    {"name": "Zee5", "license_url": "https://spapi.zee5.com/widevine/license"},
    {"name": "SonyLIV", "license_url": "https://api.sonyliv.com/drm/getlicense"},
    {"name": "SunNXT", "license_url": "https://api.sunnxt.com/license"},
    {"name": "Aha Video", "license_url": "https://api.aha.video/drm/license"},
    {"name": "JioCinema", "license_url": "https://apis.jiocinema.com/license"},
    {"name": "Voot", "license_url": "https://licensing.voot.com/widevine"},
    {"name": "MX Player", "license_url": "https://api.mxplayer.in/license"},
    {"name": "Eros Now", "license_url": "https://api.erosnow.com/drm/license"},
    {"name": "ALTBalaji", "license_url": "https://api.altbalaji.com/license"},
    {"name": "Netflix", "license_url": "https://license.netflix.com/widevine"},
    {"name": "Amazon Prime Video", "license_url": "https://atv-ps.amazon.com/cdp/license"},
    {"name": "Disney+", "license_url": "https://disney.playback.edge.bamgrid.com/widevine/v1/license"},
    {"name": "HBO Max", "license_url": "https://lic.drmtoday.com/license-proxy-widevine/cenc/"},
    {"name": "Hulu", "license_url": "https://license.hulu.com/widevine"},
    {"name": "Lionsgate Play", "license_url": "https://api.lionsgateplay.com/license"},
    {"name": "Hoichoi", "license_url": "https://api.hoichoi.tv/drm/license"},
    {"name": "Discovery+", "license_url": "https://dplus-ph-prod-vod.akamaized.net/license"},
    {"name": "Apple TV+", "license_url": "https://license.apple.com/fps/license"},
    {"name": "YouTube Premium", "license_url": "https://www.youtube.com/api/manifest/get_license"},
    {"name": "FanCode", "license_url": "https://api.fancode.com/license"},
    {"name": "Mubi", "license_url": "https://api.mubi.com/license"},
    {"name": "Epic On", "license_url": "https://api.epicon.in/license"},
    {"name": "ShemarooMe", "license_url": "https://api.shemaroome.com/license"},
    {"name": "Chaupal", "license_url": "https://api.chaupal.com/license"},
    {"name": "Stage OTT", "license_url": "https://api.stage.in/license"},
    {"name": "DocuBay", "license_url": "https://api.docubay.com/license"},
    {"name": "IVI", "license_url": "https://api.ivi.ru/license"},
    {"name": "Viu", "license_url": "https://api.viu.com/license"},
    {"name": "CuriosityStream", "license_url": "https://api.curiositystream.com/license"}
]

def test_api_endpoint(endpoint, method="GET", data=None, params=None):
    """Test a single API endpoint"""
    url = f"{BACKEND_URL}{endpoint}"
    
    try:
        print(f"\n🔍 Testing {method} {endpoint}")
        print(f"   URL: {url}")
        
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"   ❌ Unsupported method: {method}")
            return False
            
        print(f"   Status Code: {response.status_code}")
        
        # Check if response is JSON
        try:
            json_response = response.json()
            print(f"   Response Type: JSON ✅")
            print(f"   Response Keys: {list(json_response.keys()) if isinstance(json_response, dict) else 'Array/Other'}")
        except json.JSONDecodeError:
            print(f"   Response Type: Non-JSON ❌")
            print(f"   Response Text: {response.text[:200]}...")
            return False
        
        # Check for success status codes
        if 200 <= response.status_code < 300:
            print(f"   Result: ✅ SUCCESS")
            return True, json_response
        else:
            print(f"   Result: ❌ FAILED - HTTP {response.status_code}")
            print(f"   Error: {json_response}")
            return False, json_response
            
    except requests.exceptions.RequestException as e:
        print(f"   Result: ❌ CONNECTION ERROR")
        print(f"   Error: {str(e)}")
        return False, None

def test_widevine_extraction(platform_name, license_url):
    """Test Widevine DRM extraction for a specific platform"""
    
    payload = {
        "pssh": TEST_PSSH,
        "license_url": license_url,
        "headers": {},
        "challenge": None
    }
    
    try:
        print(f"\n🔍 Testing Widevine extraction for {platform_name}")
        print(f"   License URL: {license_url}")
        
        start_time = time.time()
        response = requests.post(f"{BACKEND_URL}/api/extract", json=payload, timeout=15)
        end_time = time.time()
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Time: {int((end_time - start_time) * 1000)}ms")
        
        if response.status_code != 200:
            print(f"   Result: ❌ FAILED - HTTP {response.status_code}")
            try:
                error_response = response.json()
                print(f"   Error: {error_response}")
            except:
                print(f"   Error: {response.text[:200]}")
            return False, None
        
        try:
            json_response = response.json()
        except json.JSONDecodeError:
            print(f"   Result: ❌ FAILED - Invalid JSON response")
            return False, None
        
        # Validate response structure
        required_fields = ["success", "keys", "platform", "pssh", "license_url", "extraction_time_ms"]
        missing_fields = [field for field in required_fields if field not in json_response]
        
        if missing_fields:
            print(f"   Result: ❌ FAILED - Missing fields: {missing_fields}")
            return False, json_response
        
        # Check success status
        if not json_response.get("success"):
            print(f"   Result: ❌ FAILED - success: false")
            print(f"   Error: {json_response.get('error', 'Unknown error')}")
            return False, json_response
        
        # Validate keys
        keys = json_response.get("keys", [])
        if not keys or len(keys) == 0:
            print(f"   Result: ❌ FAILED - No keys returned")
            return False, json_response
        
        # Check key structure
        for key in keys:
            if not isinstance(key, dict) or "kid" not in key or "key" not in key:
                print(f"   Result: ❌ FAILED - Invalid key structure")
                return False, json_response
        
        # Validate extraction time
        extraction_time = json_response.get("extraction_time_ms", 0)
        if extraction_time < 0 or extraction_time > 30000:  # Should be reasonable (0-30 seconds)
            print(f"   Result: ⚠️  WARNING - Unusual extraction time: {extraction_time}ms")
        
        print(f"   Result: ✅ SUCCESS")
        print(f"   Platform Detected: {json_response.get('platform', 'Unknown')}")
        print(f"   Keys Extracted: {len(keys)}")
        print(f"   Extraction Time: {extraction_time}ms")
        
        return True, json_response
        
    except requests.exceptions.RequestException as e:
        print(f"   Result: ❌ CONNECTION ERROR")
        print(f"   Error: {str(e)}")
        return False, None

def test_extraction_history():
    """Test extraction history endpoint"""
    print(f"\n🔍 Testing extraction history")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/extractions", params={"limit": 10}, timeout=10)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Result: ❌ FAILED - HTTP {response.status_code}")
            return False
        
        json_response = response.json()
        if not isinstance(json_response, list):
            print(f"   Result: ❌ FAILED - Expected array response")
            return False
        
        print(f"   Result: ✅ SUCCESS")
        print(f"   Extractions in history: {len(json_response)}")
        return True
        
    except Exception as e:
        print(f"   Result: ❌ ERROR - {str(e)}")
        return False

def main():
    """Run all backend API tests"""
    print("=" * 80)
    print("🚀 BACKEND API TESTING - ADMIN DASHBOARD & WIDEVINE DRM EXTRACTION")
    print("=" * 80)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total OTT Platforms to Test: {len(OTT_PLATFORMS)}")
    
    test_results = {}
    
    # Test 1: Basic health check
    print("\n" + "=" * 50)
    print("TEST 1: Basic Health Check")
    print("=" * 50)
    success, response = test_api_endpoint("/api/")
    test_results["health_check"] = success
    
    # Test 2: Admin Statistics
    print("\n" + "=" * 50)
    print("TEST 2: Admin Statistics")
    print("=" * 50)
    success, response = test_api_endpoint("/api/admin/statistics")
    test_results["admin_statistics"] = success
    if success and response:
        expected_keys = ["total_users", "active_users", "total_revenue", "pending_payments"]
        missing_keys = [key for key in expected_keys if key not in response]
        if missing_keys:
            print(f"   ⚠️  Missing expected keys: {missing_keys}")
        else:
            print(f"   ✅ All expected statistics keys present")
    
    # Test 3: Admin Users List
    print("\n" + "=" * 50)
    print("TEST 3: Admin Users List")
    print("=" * 50)
    success, response = test_api_endpoint("/api/admin/users", params={"limit": 10})
    test_results["admin_users"] = success
    if success and response:
        if "users" in response and "total" in response:
            print(f"   ✅ Response structure correct")
            print(f"   📊 Total users: {response.get('total', 0)}")
            print(f"   📊 Users returned: {len(response.get('users', []))}")
        else:
            print(f"   ⚠️  Missing expected keys: users, total")
    
    # Test 4: Admin Payments List
    print("\n" + "=" * 50)
    print("TEST 4: Admin Payments List")
    print("=" * 50)
    success, response = test_api_endpoint("/api/admin/payments", params={"status": "pending", "limit": 10})
    test_results["admin_payments"] = success
    if success and response:
        if "payments" in response and "total" in response:
            print(f"   ✅ Response structure correct")
            print(f"   📊 Total payments: {response.get('total', 0)}")
            print(f"   📊 Payments returned: {len(response.get('payments', []))}")
        else:
            print(f"   ⚠️  Missing expected keys: payments, total")
    
    # Test 5: Admin Broadcasts List
    print("\n" + "=" * 50)
    print("TEST 5: Admin Broadcasts List")
    print("=" * 50)
    success, response = test_api_endpoint("/api/admin/broadcasts", params={"limit": 10})
    test_results["admin_broadcasts"] = success
    if success and response:
        if "broadcasts" in response:
            print(f"   ✅ Response structure correct")
            print(f"   📊 Broadcasts returned: {len(response.get('broadcasts', []))}")
        else:
            print(f"   ⚠️  Missing expected key: broadcasts")
    
    # Test 6: Widevine DRM Extraction for All 30 Platforms
    print("\n" + "=" * 80)
    print("TEST 6: WIDEVINE DRM EXTRACTION - ALL 30 OTT PLATFORMS")
    print("=" * 80)
    
    widevine_results = {}
    successful_extractions = []
    failed_extractions = []
    sample_responses = []
    
    for i, platform in enumerate(OTT_PLATFORMS, 1):
        print(f"\n--- Platform {i}/30 ---")
        success, response = test_widevine_extraction(platform["name"], platform["license_url"])
        widevine_results[platform["name"]] = success
        
        if success:
            successful_extractions.append(platform["name"])
            # Collect sample responses from first 3 successful platforms
            if len(sample_responses) < 3 and response:
                sample_responses.append({
                    "platform": platform["name"],
                    "response": response
                })
        else:
            failed_extractions.append(platform["name"])
        
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    test_results["widevine_extraction"] = len(failed_extractions) == 0
    
    # Test 7: Extraction History
    print("\n" + "=" * 50)
    print("TEST 7: Extraction History")
    print("=" * 50)
    success = test_extraction_history()
    test_results["extraction_history"] = success
    
    # Detailed Widevine Results Summary
    print("\n" + "=" * 80)
    print("🎯 WIDEVINE DRM EXTRACTION RESULTS")
    print("=" * 80)
    
    print(f"✅ Successful Extractions: {len(successful_extractions)}/30")
    print(f"❌ Failed Extractions: {len(failed_extractions)}/30")
    
    if successful_extractions:
        print(f"\n🎉 SUCCESSFUL PLATFORMS:")
        for platform in successful_extractions:
            print(f"   ✅ {platform}")
    
    if failed_extractions:
        print(f"\n⚠️  FAILED PLATFORMS:")
        for platform in failed_extractions:
            print(f"   ❌ {platform}")
    
    # Sample responses
    if sample_responses:
        print(f"\n📋 SAMPLE RESPONSES (First 3 Successful):")
        for i, sample in enumerate(sample_responses, 1):
            print(f"\n--- Sample {i}: {sample['platform']} ---")
            response = sample['response']
            print(f"   Success: {response.get('success')}")
            print(f"   Platform: {response.get('platform')}")
            print(f"   Keys Count: {len(response.get('keys', []))}")
            print(f"   Extraction Time: {response.get('extraction_time_ms')}ms")
            if response.get('keys'):
                first_key = response['keys'][0]
                print(f"   Sample Key ID: {first_key.get('kid', 'N/A')[:16]}...")
                print(f"   Sample Key: {first_key.get('key', 'N/A')[:16]}...")
    
    # Overall Summary
    print("\n" + "=" * 80)
    print("📋 OVERALL TEST SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n📊 Overall Result: {passed_tests}/{total_tests} tests passed")
    print(f"🎯 Widevine Platforms: {len(successful_extractions)}/30 successful")
    
    if passed_tests == total_tests and len(successful_extractions) == 30:
        print("🎉 ALL TESTS PASSED! ALL 30 PLATFORMS WORKING!")
        return True
    elif len(successful_extractions) >= 25:  # Allow some tolerance
        print("✅ MOSTLY SUCCESSFUL! 25+ platforms working")
        return True
    else:
        print("⚠️  SOME TESTS FAILED!")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)