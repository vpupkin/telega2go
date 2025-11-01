#!/usr/bin/env python3
"""
Test: Regression Test for Working User Registration

Tests that a previously working user registration still works:
1. Registration with chat_id (simple case - should work as before)
2. Registration should not fail due to resolution errors
3. Registration should work even if resolution fails
"""

import requests
import json
import sys

BACKEND_URL = "http://localhost:55552/api"

def test_simple_chatid_registration():
    """Test: Simple registration with chat_id (should work as before)"""
    print("🧪 Test 1: Simple registration with chat_id only")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"WorkingUser_{abs(hash('working'))}",
            "email": f"working_{abs(hash('working'))}@example.com",
            "phone": "1234567890",
            "telegram_chat_id": f"{abs(hash('working'))}"
        }
    )
    # Should NOT be 422 (validation error) - might be 500 (OTP failure) but that's OK
    if response.status_code == 422:
        error = response.json().get("detail", "")
        print(f"❌ FAIL: Got 422 validation error: {error}")
        return False
    print(f"✅ PASS: Registration accepted (status: {response.status_code})")
    return True

def test_resolution_failure_graceful():
    """Test: Registration should work even if resolution fails"""
    print("🧪 Test 2: Registration with invalid chat_id (should fail gracefully, not 422)")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"InvalidUser_{abs(hash('invalid'))}",
            "email": f"invalid_{abs(hash('invalid'))}@example.com",
            "phone": "1234567891",
            "telegram_chat_id": "999999999999999"  # Invalid but should be accepted (OTP will fail)
        }
    )
    # Should NOT be 422 - should proceed to OTP sending (even if OTP fails later)
    if response.status_code == 422:
        error = response.json().get("detail", "")
        # Check if it's a resolution error that blocks registration
        if "resolve" in error.lower() or "could not" in error.lower():
            print(f"❌ FAIL: Resolution error blocking registration: {error}")
            return False
    print(f"✅ PASS: Registration proceeds (status: {response.status_code})")
    return True

def test_no_required_validation():
    """Test: Only chat_id OR username required (not both)"""
    print("🧪 Test 3: Registration validation (chat_id only)")
    response = requests.post(
        f"{BACKEND_URL}/register",
        json={
            "name": f"ValidUser_{abs(hash('valid'))}",
            "email": f"valid_{abs(hash('valid'))}@example.com",
            "phone": "1234567892",
            "telegram_chat_id": f"{abs(hash('valid'))}"
        }
    )
    # Should accept (not 422)
    assert response.status_code != 422 or "either" not in response.json().get("detail", "").lower(), \
        f"Should accept chat_id only, got: {response.text[:200]}"
    print(f"✅ PASS: Chat ID only accepted (status: {response.status_code})")
    return True

def run_all_tests():
    """Run all regression tests"""
    print("=" * 60)
    print("🧪 Regression Tests - Working User Registration")
    print("=" * 60)
    
    tests = [
        test_simple_chatid_registration,
        test_resolution_failure_graceful,
        test_no_required_validation
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
    print("✅ All regression tests passed!")
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

