#!/usr/bin/env python3
"""
Test: Username-Only Registration for geshatele
Tests that username-only registration works via sendMessage resolution
"""

import requests
import json
import sys

BASE_URL = "http://localhost:55552/api"
GESHATELE_USERNAME = "@geshatele"

def test_username_only_registration():
    """Test: Registration with ONLY username (should resolve via sendMessage)"""
    print("🧪 Test: Username-Only Registration (@geshatele)")
    print("=" * 60)
    
    payload = {
        "name": "geshatele_username_only",
        "email": f"geshatele_username_{int(__import__('time').time())}@test.com",
        "phone": "1234567890",
        "telegram_username": GESHATELE_USERNAME
    }
    
    print(f"📤 Payload: {json.dumps(payload, indent=2)}")
    print(f"📤 Testing username-only registration for: {GESHATELE_USERNAME}")
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=payload)
        print(f"📥 Status: {response.status_code}")
        print(f"📥 Response: {response.text[:200]}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Username-only registration worked!")
            print("   Backend successfully resolved username → chat_id via sendMessage")
            return True
        elif response.status_code == 422:
            data = response.json()
            detail = data.get("detail", "")
            if "resolve" in detail.lower() or "not found" in detail.lower():
                print(f"⚠️  Username resolution failed: {detail}")
                print("   This is expected if bot cannot message the user or username doesn't exist")
                return False
            else:
                print(f"❌ Unexpected 422: {detail}")
                return False
        elif response.status_code == 400:
            data = response.json()
            detail = data.get("detail", "")
            if "already registered" in detail.lower():
                print("✅ EXPECTED: User already registered (correct behavior)")
                return True
            else:
                print(f"⚠️  400 Error: {detail}")
                return False
        else:
            print(f"⚠️  Status {response.status_code}: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Username-Only Registration")
    print("=" * 60)
    
    success = test_username_only_registration()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULT:")
    print(f"  {'✅ PASSED' if success else '❌ FAILED'}")
    
    sys.exit(0 if success else 1)

