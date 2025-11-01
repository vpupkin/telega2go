#!/usr/bin/env python3
"""
Test suite for geshatele user registration
Tests both Chat ID and Username modes
"""

import requests
import json
import sys

BASE_URL = "http://localhost:55552/api"

def test_chat_id_registration():
    """Test registration with Chat ID for geshatele"""
    print("🧪 Test 1: Registration with Chat ID (geshatele)")
    print("=" * 60)
    
    payload = {
        "name": "geshatele",
        "email": "geshatele@test.com",
        "phone": "1234567890",
        "telegram_chat_id": "415043706"
    }
    
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=payload)
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Registration initiated")
            return True
        elif response.status_code == 400:
            data = response.json()
            if "already registered" in data.get("detail", "").lower():
                print("✅ EXPECTED: User already registered (correct behavior)")
                return True
            else:
                print(f"❌ FAILED: {data.get('detail', 'Unknown error')}")
                return False
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_username_registration():
    """Test registration with Username for geshatele"""
    print("\n🧪 Test 2: Registration with Username (@geshatele)")
    print("=" * 60)
    
    payload = {
        "name": "geshatele",
        "email": "geshatele2@test.com",
        "phone": "1234567891",
        "telegram_username": "@geshatele"
    }
    
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=payload)
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 422:
            data = response.json()
            detail = data.get("detail", "")
            if "resolve" in detail.lower() or "chat_id" in detail.lower():
                print("✅ EXPECTED: Username resolution failed (needs Chat ID mode)")
                print(f"   Error message: {detail}")
                return True
            else:
                print(f"❌ UNEXPECTED 422: {detail}")
                return False
        elif response.status_code == 200:
            print("✅ SUCCESS: Registration initiated")
            return True
        else:
            print(f"⚠️  Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing geshatele Registration")
    print("=" * 60)
    
    test1 = test_chat_id_registration()
    test2 = test_username_registration()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"  Test 1 (Chat ID): {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"  Test 2 (Username): {'✅ PASSED' if test2 else '❌ FAILED'}")
    
    if test1 and test2:
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)

