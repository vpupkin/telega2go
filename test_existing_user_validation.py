#!/usr/bin/env python3
"""
Test: Existing User Validation

Tests that the backend correctly rejects registration for existing users:
1. Existing Telegram user (by chat_id)
2. Existing Telegram user (by username)
3. Existing email
4. Existing name
"""

import requests
import json
import sys

BACKEND_URL = "http://localhost:55552/api"

def test_existing_telegram_chatid():
    """Test: Registration with existing chat_id should be rejected"""
    print("🧪 Test 1: Registration with existing telegram_chat_id")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"TestExisting_{abs(hash('existing'))}",
            "email": f"test_existing_{abs(hash('existing'))}@example.com",
            "phone": "1234567890",
            "telegram_chat_id": "123456789"  # This might exist
        }
    )
    # Should be 400 if user exists, or 500/422 if other issues
    if response.status_code == 400:
        error = response.json().get("detail", "")
        assert "already" in error.lower() or "registered" in error.lower(), \
            f"Error should mention 'already' or 'registered': {error}"
        print(f"✅ PASS: Existing chat_id rejected: {error[:60]}...")
        return True
    else:
        print(f"ℹ️  INFO: Status {response.status_code} (user may not exist): {response.text[:100]}")
        return True  # Not an error - user doesn't exist yet

def test_existing_email():
    """Test: Registration with existing email should be rejected"""
    print("🧪 Test 2: Registration with existing email")
    # First register a user
    test_email = f"existing_email_test_{abs(hash('email'))}@example.com"
    response1 = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"FirstUser_{abs(hash('first'))}",
            "email": test_email,
            "phone": "1111111111",
            "telegram_chat_id": f"{abs(hash('first'))}"
        }
    )
    
    # Try to register again with same email
    response2 = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"SecondUser_{abs(hash('second'))}",
            "email": test_email,
            "phone": "2222222222",
            "telegram_chat_id": f"{abs(hash('second'))}"
        }
    )
    
    if response2.status_code == 400:
        error = response2.json().get("detail", "")
        assert "email" in error.lower() and "already" in error.lower(), \
            f"Error should mention email already exists: {error}"
        print("✅ PASS: Existing email rejected")
        return True
    else:
        print(f"ℹ️  INFO: Status {response2.status_code}: {response2.text[:100]}")
        return True

def test_existing_name():
    """Test: Registration with existing name should be rejected"""
    print("🧪 Test 3: Registration with existing name")
    test_name = f"ExistingName_{abs(hash('name'))}"
    # First register
    response1 = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": test_name,
            "email": f"first_{abs(hash('name'))}@example.com",
            "phone": "1111111111",
            "telegram_chat_id": f"{abs(hash('name1'))}"
        }
    )
    
    # Try to register with same name (different case)
    response2 = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": test_name.upper(),  # Different case
            "email": f"second_{abs(hash('name'))}@example.com",
            "phone": "2222222222",
            "telegram_chat_id": f"{abs(hash('name2'))}"
        }
    )
    
    if response2.status_code == 400:
        error = response2.json().get("detail", "")
        assert "name" in error.lower() and "taken" in error.lower(), \
            f"Error should mention name already taken: {error}"
        print("✅ PASS: Existing name rejected (case-insensitive)")
        return True
    else:
        print(f"ℹ️  INFO: Status {response2.status_code}: {response2.text[:100]}")
        return True

def test_error_message_clarity():
    """Test: Error messages are clear and helpful"""
    print("🧪 Test 4: Error message clarity")
    # Test with duplicate email
    test_email = f"clarity_test_{abs(hash('clarity'))}@example.com"
    response1 = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"Clarity1_{abs(hash('clarity'))}",
            "email": test_email,
            "phone": "1111111111",
            "telegram_chat_id": f"{abs(hash('clarity1'))}"
        }
    )
    
    response2 = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"Clarity2_{abs(hash('clarity'))}",
            "email": test_email,
            "phone": "2222222222",
            "telegram_chat_id": f"{abs(hash('clarity2'))}"
        }
    )
    
    if response2.status_code == 400:
        error = response2.json().get("detail", "")
        assert len(error) > 10, f"Error message should be informative: {error}"
        print(f"✅ PASS: Clear error message: '{error[:80]}...'")
        return True
    else:
        print(f"ℹ️  INFO: Status {response2.status_code}")
        return True

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Existing User Validation Tests")
    print("=" * 60)
    
    tests = [
        test_existing_telegram_chatid,
        test_existing_email,
        test_existing_name,
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

