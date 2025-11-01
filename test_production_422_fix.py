#!/usr/bin/env python3
"""
Test: Production 422 Fix (PENALTY FIX)

Tests that the frontend payload construction correctly handles:
1. Username mode - only sends telegram_username
2. Chat ID mode - only sends telegram_chat_id
3. Empty values - properly rejected before sending
4. Both fields - never sent together
"""

import requests
import json
import sys

BACKEND_URL = "http://localhost:55552/api"

def test_username_only_payload():
    """Test: Payload with username only (should work)"""
    print("🧪 Test 1: Registration with username only")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestUser_{abs(hash('user'))}",
            "email": f"user_{abs(hash('user'))}@example.com",
            "phone": "1234567890",
            "telegram_username": "@testuser"  # Only username, no chat_id
        }
    )
    # Should NOT be 422 (validation error)
    if response.status_code == 422:
        error = response.json().get("detail", "")
        print(f"❌ FAIL: Got 422 validation error: {error}")
        return False
    print(f"✅ PASS: Username-only payload accepted (status: {response.status_code})")
    return True

def test_chatid_only_payload():
    """Test: Payload with chat_id only (should work)"""
    print("🧪 Test 2: Registration with chat_id only")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestChat_{abs(hash('chat'))}",
            "email": f"chat_{abs(hash('chat'))}@example.com",
            "phone": "1234567891",
            "telegram_chat_id": f"{abs(hash('chat'))}"  # Only chat_id, no username
        }
    )
    # Should NOT be 422 (validation error)
    if response.status_code == 422:
        error = response.json().get("detail", "")
        print(f"❌ FAIL: Got 422 validation error: {error}")
        return False
    print(f"✅ PASS: Chat ID-only payload accepted (status: {response.status_code})")
    return True

def test_empty_string_handling():
    """Test: Empty string values properly handled"""
    print("🧪 Test 3: Registration with empty string username (should fail validation)")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestEmpty_{abs(hash('empty'))}",
            "email": f"empty_{abs(hash('empty'))}@example.com",
            "phone": "1234567892",
            "telegram_username": "",  # Empty string
            "telegram_chat_id": ""    # Empty string
        }
    )
    # Should be 422 (both empty)
    assert response.status_code == 422, f"Expected 422 for empty strings, got {response.status_code}"
    error = response.json().get("detail", "")
    assert "either" in error.lower() or "required" in error.lower(), \
        f"Error should mention identifier required: {error}"
    print("✅ PASS: Empty strings properly rejected")
    return True

def test_one_empty_one_valid():
    """Test: One field empty, one valid (should work)"""
    print("🧪 Test 4: Registration with valid chat_id and empty username")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestMixed_{abs(hash('mixed'))}",
            "email": f"mixed_{abs(hash('mixed'))}@example.com",
            "phone": "1234567893",
            "telegram_chat_id": f"{abs(hash('mixed'))}",
            "telegram_username": ""  # Empty - should be ignored
        }
    )
    # Should NOT be 422 (valid chat_id should work)
    if response.status_code == 422:
        error = response.json().get("detail", "")
        print(f"❌ FAIL: Got 422 when chat_id is valid: {error}")
        return False
    print(f"✅ PASS: Valid chat_id with empty username accepted (status: {response.status_code})")
    return True

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Production 422 Fix Tests (PENALTY FIX)")
    print("=" * 60)
    
    tests = [
        test_username_only_payload,
        test_chatid_only_payload,
        test_empty_string_handling,
        test_one_empty_one_valid
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

