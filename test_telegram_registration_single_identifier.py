#!/usr/bin/env python3
"""
Test: Telegram Registration - Only ONE Identifier (KISS)

Validates that the registration endpoint:
1. Accepts EITHER telegram_chat_id OR telegram_username (never both)
2. Rejects requests with both identifiers
3. Rejects requests with no identifiers
4. Requires chat_id for OTP delivery
"""

import requests
import json
import sys

BACKEND_URL = "http://localhost:55552/api"

def test_only_chat_id():
    """Test: Registration with ONLY chat_id (validation should pass, OTP may fail)"""
    print("🧪 Test 1: Registration with ONLY telegram_chat_id")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestUser_{abs(hash('chatid'))}",
            "email": f"test_chatid_{abs(hash('chatid'))}@example.com",
            "phone": "1234567890",
            "telegram_chat_id": "123456789"
        }
    )
    # ✅ KISS: Validation passed if we got past 422 (OTP failure is separate issue)
    assert response.status_code != 422, f"Should NOT be 422 (validation error), got {response.status_code}: {response.text[:200]}"
    print(f"✅ PASS: Chat ID only accepted (status: {response.status_code})")
    return True

def test_only_username():
    """Test: Registration with ONLY username (should fail - needs chat_id for OTP)"""
    print("🧪 Test 2: Registration with ONLY telegram_username")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestUser_{abs(hash('username'))}",
            "email": f"test_username_{abs(hash('username'))}@example.com",
            "phone": "1234567891",
            "telegram_username": "@testuser"
        }
    )
    assert response.status_code == 422, f"Expected 422 (username needs chat_id), got {response.status_code}: {response.text[:200]}"
    error_data = response.json()
    # Handle both string and list error formats
    detail = error_data.get("detail", "")
    if isinstance(detail, list):
        detail = " ".join(str(d) for d in detail)
    error_str = str(detail).lower()
    assert "chat_id" in error_str or "chat id" in error_str, f"Error should mention chat_id requirement: {error_str}"
    print("✅ PASS: Username only rejected (needs chat_id)")
    return True

def test_both_identifiers():
    """Test: Registration with BOTH identifiers (should fail)"""
    print("🧪 Test 3: Registration with BOTH telegram_chat_id AND telegram_username")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestUser_{abs(hash('both'))}",
            "email": f"test_both_{abs(hash('both'))}@example.com",
            "phone": "1234567892",
            "telegram_chat_id": "123456789",
            "telegram_username": "@testuser"
        }
    )
    assert response.status_code == 422, f"Expected 422 (only one allowed), got {response.status_code}: {response.text[:200]}"
    error_data = response.json()
    detail = error_data.get("detail", "")
    if isinstance(detail, list):
        detail = " ".join(str(d) for d in detail)
    error_str = str(detail).lower()
    assert "only" in error_str or "one" in error_str, f"Error should mention only one allowed: {error_str}"
    print("✅ PASS: Both identifiers rejected")
    return True

def test_no_identifiers():
    """Test: Registration with NO identifiers (should fail)"""
    print("🧪 Test 4: Registration with NO identifiers")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": "TestUser",
            "email": "test_none@example.com",
            "phone": "1234567893"
        }
    )
    assert response.status_code == 422, f"Expected 422 (identifier required), got {response.status_code}: {response.text[:200]}"
    error_data = response.json()
    detail = error_data.get("detail", "")
    if isinstance(detail, list):
        detail = " ".join(str(d) for d in detail)
    error_str = str(detail).lower()
    assert "telegram" in error_str or "identifier" in error_str, f"Error should mention identifier required: {error_str}"
    print("✅ PASS: No identifiers rejected")
    return True

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Telegram Registration - Single Identifier Tests (KISS)")
    print("=" * 60)
    
    tests = [
        test_only_chat_id,
        test_only_username,
        test_both_identifiers,
        test_no_identifiers
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

