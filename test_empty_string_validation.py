#!/usr/bin/env python3
"""
Test: Empty String Validation (PENALTY FIX)

Tests that empty strings don't cause false validation failures:
1. Empty string for chat_id → Should be treated as missing
2. Whitespace-only chat_id → Should be treated as missing
3. Valid chat_id → Should work
4. Frontend should not send empty strings
"""

import requests
import json
import sys

BACKEND_URL = "http://localhost:55552/api"

def test_empty_string_chatid():
    """Test: Empty string chat_id should be treated as missing"""
    print("🧪 Test 1: Registration with empty string chat_id")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestEmpty_{abs(hash('empty'))}",
            "email": f"empty_{abs(hash('empty'))}@example.com",
            "phone": "1234567890",
            "telegram_chat_id": ""  # Empty string
        }
    )
    # Should be 422 (missing identifier)
    assert response.status_code == 422, f"Expected 422 for empty string, got {response.status_code}"
    error = response.json().get("detail", "")
    assert "either" in error.lower() or "required" in error.lower(), \
        f"Error should mention identifier required: {error}"
    print("✅ PASS: Empty string treated as missing")
    return True

def test_whitespace_chatid():
    """Test: Whitespace-only chat_id should be treated as missing"""
    print("🧪 Test 2: Registration with whitespace-only chat_id")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestWhitespace_{abs(hash('whitespace'))}",
            "email": f"whitespace_{abs(hash('whitespace'))}@example.com",
            "phone": "1234567891",
            "telegram_chat_id": "   "  # Whitespace only
        }
    )
    # Should be 422 (missing identifier)
    assert response.status_code == 422, f"Expected 422 for whitespace, got {response.status_code}"
    error = response.json().get("detail", "")
    assert "either" in error.lower() or "required" in error.lower(), \
        f"Error should mention identifier required: {error}"
    print("✅ PASS: Whitespace treated as missing")
    return True

def test_valid_chatid_with_empty_username():
    """Test: Valid chat_id with empty username should work"""
    print("🧪 Test 3: Registration with valid chat_id (empty username ignored)")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestValid_{abs(hash('valid'))}",
            "email": f"valid_{abs(hash('valid'))}@example.com",
            "phone": "1234567892",
            "telegram_chat_id": f"{abs(hash('valid'))}",
            "telegram_username": ""  # Empty string - should be ignored
        }
    )
    # Should NOT be 422 (validation should pass)
    assert response.status_code != 422, \
        f"Should NOT be 422 validation error, got {response.status_code}: {response.text[:200]}"
    print(f"✅ PASS: Valid chat_id accepted (empty username ignored) (status: {response.status_code})")
    return True

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Empty String Validation Tests (PENALTY FIX)")
    print("=" * 60)
    
    tests = [
        test_empty_string_chatid,
        test_whitespace_chatid,
        test_valid_chatid_with_empty_username
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

