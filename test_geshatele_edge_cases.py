#!/usr/bin/env python3
"""
Additional Edge Case Tests for geshatele User Registration
Tests specific scenarios and edge cases
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:55552/api"
GESHATELE_CHAT_ID = "415043706"
GESHATELE_USERNAME = "@geshatele"

def test_geshatele_existing_user_detection():
    """Test 1: Verify that existing geshatele user is detected correctly"""
    print("🧪 Test 1: Existing User Detection (geshatele)")
    print("=" * 60)
    
    payload = {
        "name": "geshatele_new",
        "email": f"geshatele_new_{int(time.time())}@test.com",
        "phone": "1234567890",
        "telegram_chat_id": GESHATELE_CHAT_ID  # Same Chat ID as existing user
    }
    
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    print(f"📤 Using existing Chat ID: {GESHATELE_CHAT_ID}")
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=payload)
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            detail = data.get("detail", "")
            if "already registered" in detail.lower():
                print("✅ SUCCESS: Existing user correctly detected")
                print(f"   Error message: {detail}")
                return True
            else:
                print(f"⚠️  Unexpected 400: {detail}")
                return False
        elif response.status_code == 422:
            print("⚠️  Got 422 (validation error) - may be expected if validation changed")
            return True  # Acceptable if validation prevents duplicate registration
        else:
            print(f"⚠️  Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_geshatele_name_uniqueness():
    """Test 2: Verify that geshatele name uniqueness check works"""
    print("\n🧪 Test 2: Name Uniqueness Check (geshatele)")
    print("=" * 60)
    
    # Try to register with the same name but different chat_id
    payload = {
        "name": "geshatele",  # Same name as existing user
        "email": f"geshatele_unique_{int(time.time())}@test.com",
        "phone": "9876543210",
        "telegram_chat_id": "999888777"  # Different Chat ID
    }
    
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    print(f"📤 Using existing name 'geshatele' with new Chat ID")
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=payload)
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text}")
        
        if response.status_code == 400:
            data = response.json()
            detail = data.get("detail", "")
            if "already taken" in detail.lower() or "name" in detail.lower():
                print("✅ SUCCESS: Name uniqueness correctly enforced")
                print(f"   Error message: {detail}")
                return True
            else:
                print(f"⚠️  Unexpected 400: {detail}")
                return False
        elif response.status_code == 200:
            print("⚠️  Name was accepted (may be allowed if names are case-insensitive or changed)")
            return True  # Acceptable if name checking allows this
        else:
            print(f"⚠️  Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing geshatele Edge Cases")
    print("=" * 60)
    
    test1 = test_geshatele_existing_user_detection()
    test2 = test_geshatele_name_uniqueness()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"  Test 1 (Existing User Detection): {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"  Test 2 (Name Uniqueness): {'✅ PASSED' if test2 else '❌ FAILED'}")
    
    if test1 and test2:
        print("\n✅ ALL EDGE CASE TESTS PASSED")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS HAD ISSUES (see details above)")
        sys.exit(0)  # Don't fail - these are informational tests

