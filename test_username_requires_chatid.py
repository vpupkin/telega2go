#!/usr/bin/env python3
"""
Test: Username Requires Chat ID for OTP Delivery

Validates that:
1. Username-only registration is rejected (needs chat_id for OTP)
2. Username + chat_id registration is accepted (both provided)
3. Chat ID-only registration is accepted (pure chat_id)
4. Error messages are clear about chat_id requirement
"""

import requests
import json
import sys

BACKEND_URL = "http://localhost:55552/api"

def test_username_only_rejected():
    """Test: Username-only should be rejected (needs chat_id for OTP)"""
    print("🧪 Test 1: Registration with ONLY username (should be rejected)")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestUser_{abs(hash('useronly'))}",
            "email": f"test_useronly_{abs(hash('useronly'))}@example.com",
            "phone": "1234567890",
            "telegram_username": "@testuser"
        }
    )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text[:200]}"
    error_data = response.json()
    detail = error_data.get("detail", "")
    if isinstance(detail, list):
        detail = " ".join(str(d) for d in detail)
    error_str = str(detail).lower()
    assert "chat_id" in error_str, f"Error should mention chat_id requirement: {error_str}"
    assert "otp" in error_str or "required" in error_str, f"Error should mention OTP/required: {error_str}"
    print("✅ PASS: Username-only rejected (needs chat_id)")
    return True

def test_username_with_chatid_accepted():
    """Test: Username + chat_id should be accepted (both provided)"""
    print("🧪 Test 2: Registration with username + chat_id (should be accepted)")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestUser_{abs(hash('userchat'))}",
            "email": f"test_userchat_{abs(hash('userchat'))}@example.com",
            "phone": "1234567891",
            "telegram_username": "@testuser",
            "telegram_chat_id": "123456789"
        }
    )
    # ✅ Validation should pass (OTP may fail, but that's separate)
    assert response.status_code != 422, f"Should NOT be 422 (validation error), got {response.status_code}: {response.text[:200]}"
    print(f"✅ PASS: Username + chat_id accepted (status: {response.status_code})")
    return True

def test_chatid_only_accepted():
    """Test: Chat ID-only should be accepted (pure chat_id)"""
    print("🧪 Test 3: Registration with ONLY chat_id (should be accepted)")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestUser_{abs(hash('chatidonly'))}",
            "email": f"test_chatidonly_{abs(hash('chatidonly'))}@example.com",
            "phone": "1234567892",
            "telegram_chat_id": "123456789"
        }
    )
    # ✅ Validation should pass (OTP may fail, but that's separate)
    assert response.status_code != 422, f"Should NOT be 422 (validation error), got {response.status_code}: {response.text[:200]}"
    print(f"✅ PASS: Chat ID-only accepted (status: {response.status_code})")
    return True

def test_error_message_clarity():
    """Test: Error message should clearly state chat_id requirement"""
    print("🧪 Test 4: Error message clarity for username-only")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": "TestUser",
            "email": "test_error@example.com",
            "phone": "1234567893",
            "telegram_username": "@testuser"
        }
    )
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    error_data = response.json()
    detail = error_data.get("detail", "")
    if isinstance(detail, list):
        detail = " ".join(str(d) for d in detail)
    error_str = str(detail)
    # Check for clear messaging
    assert "chat_id" in error_str.lower() or "chat id" in error_str.lower(), f"Error should mention chat_id: {error_str}"
    assert "otp" in error_str.lower() or "required" in error_str.lower(), f"Error should mention OTP/required: {error_str}"
    print(f"✅ PASS: Error message is clear: '{error_str[:80]}...'")
    return True

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Username Requires Chat ID for OTP - Tests")
    print("=" * 60)
    
    tests = [
        test_username_only_rejected,
        test_username_with_chatid_accepted,
        test_chatid_only_accepted,
        test_error_message_clarity
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ FAIL: {test.__name__}: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    if failed > 0:
        print(f"❌ {failed} tests failed")
        return False
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

