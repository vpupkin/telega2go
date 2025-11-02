#!/usr/bin/env python3
"""
Test: Resend OTP for username-only registration
Tests that resend-otp works with username-only sessions
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:55552/api"

def test_resend_otp_username_only():
    """Test: Resend OTP for username-only registration session"""
    print("🧪 Test: Resend OTP (Username-Only Registration)")
    print("=" * 60)
    
    # First, create a registration session with username only
    register_payload = {
        "name": f"test_resend_{int(time.time())}",
        "email": f"test_resend_{int(time.time())}@test.com",
        "phone": "1234567890",
        "telegram_username": "@geshatele"
    }
    
    print("📤 Step 1: Creating registration session with username-only...")
    register_response = requests.post(f"{BASE_URL}/register", json=register_payload)
    print(f"   Status: {register_response.status_code}")
    
    if register_response.status_code != 200:
        print(f"   ❌ Registration failed: {register_response.text}")
        return False
    
    email = register_payload["email"]
    print(f"   ✅ Registration session created for: {email}")
    
    # Now try to resend OTP
    print(f"\n📤 Step 2: Resending OTP to {email}...")
    resend_payload = {
        "email": email
    }
    
    resend_response = requests.post(
        f"{BASE_URL}/resend-otp",
        json=resend_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📥 Status: {resend_response.status_code}")
    print(f"📥 Response: {resend_response.text[:200]}")
    
    if resend_response.status_code == 200:
        data = resend_response.json()
        print("✅ SUCCESS: OTP resent successfully!")
        if data.get("requires_bot_start"):
            print("   ℹ️  OTP may not be delivered (user needs to start bot)")
        return True
    elif resend_response.status_code == 422:
        data = resend_response.json()
        detail = data.get("detail", "")
        if "Email is required" in detail or "email" in detail.lower():
            print("❌ FAILED: Email validation error (wrong parameter format)")
            return False
        else:
            print(f"⚠️  422 Error: {detail}")
            return False
    else:
        print(f"❌ FAILED: Status {resend_response.status_code}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Resend OTP (Username-Only)")
    print("=" * 60)
    
    success = test_resend_otp_username_only()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULT:")
    print(f"  {'✅ PASSED' if success else '❌ FAILED'}")
    
    sys.exit(0 if success else 1)



