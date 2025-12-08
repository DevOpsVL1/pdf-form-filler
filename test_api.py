#!/usr/bin/env python3
"""
Test Flask API directly (without browser)
Run this while Flask server is running in another terminal
"""

import requests
import json

print("=" * 60)
print("API TEST - Testing Flask endpoints")
print("=" * 60)

# Configuration
BASE_URL = "http://localhost:5000"

# Test data
cif1_data = {
    'ic_number': '920315105438',
    'name_ic': 'AHMAD FARIZ BIN ABDULLAH'
}

print("\n1. Testing CIF-1 API endpoint...")
print(f"   URL: {BASE_URL}/api/generate/cif1")
print(f"   Data: {cif1_data}")

try:
    response = requests.post(
        f"{BASE_URL}/api/generate/cif1",
        json=cif1_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\n   Response Status: {response.status_code}")
    print(f"   Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print(f"   ✓ SUCCESS! PDF Size: {len(response.content)} bytes")
        print(f"   ✓ Content-Type: {response.headers.get('Content-Type')}")
        
        # Save PDF to file
        with open('test_cif1.pdf', 'wb') as f:
            f.write(response.content)
        print(f"   ✓ Saved to: test_cif1.pdf")
    else:
        print(f"   ✗ FAILED!")
        print(f"   Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("   ✗ ERROR: Cannot connect to Flask server!")
    print("   Make sure Flask is running: python app.py")
    exit(1)
except Exception as e:
    print(f"   ✗ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("If API test works but browser doesn't, issue is in JavaScript")
print("If API test fails, issue is in Flask backend")
print("=" * 60)
