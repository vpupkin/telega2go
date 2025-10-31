"""
PENALTY TEST 2: Test register_telegram_user endpoint validation and error handling
Tests that the endpoint properly validates password and handles registration requests
"""
import pytest
import asyncio
import httpx
import os

# Test against local backend (✅ Correct port: 55552 from docker-compose.yml)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:55552")
API_BASE = f"{BACKEND_URL}/api"

async def test_register_telegram_password_validation():
    """Test that password validation works correctly (min 6 characters)"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Password too short
        response = await client.post(
            f"{API_BASE}/register-telegram",
            json={
                "urr_id": "test-urr-id-123",
                "password": "12345",  # Only 5 characters
                "username": "testuser"
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "Password must be at least 6 characters" in response.json().get("detail", ""), \
            f"Expected password validation error, got: {response.json()}"
        print("✅ Test 1 passed: Password too short rejected")
        
        # Test 2: Empty password
        response = await client.post(
            f"{API_BASE}/register-telegram",
            json={
                "urr_id": "test-urr-id-123",
                "password": "",  # Empty
                "username": "testuser"
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "Password must be at least 6 characters" in response.json().get("detail", ""), \
            f"Expected password validation error, got: {response.json()}"
        print("✅ Test 2 passed: Empty password rejected")
        
        # Test 3: Missing password field
        response = await client.post(
            f"{API_BASE}/register-telegram",
            json={
                "urr_id": "test-urr-id-123",
                "username": "testuser"
                # password missing
            }
        )
        assert response.status_code == 422, f"Expected 422 (validation error), got {response.status_code}"
        print("✅ Test 3 passed: Missing password field rejected")

async def test_register_telegram_missing_urr_id():
    """Test that missing or invalid URR_ID returns proper error"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test 1: Missing URR_ID
        response = await client.post(
            f"{API_BASE}/register-telegram",
            json={
                "password": "validpassword123",
                "username": "testuser"
                # urr_id missing
            }
        )
        assert response.status_code == 422, f"Expected 422 (validation error), got {response.status_code}"
        print("✅ Test 1 passed: Missing URR_ID rejected")
        
        # Test 2: Invalid/non-existent URR_ID
        response = await client.post(
            f"{API_BASE}/register-telegram",
            json={
                "urr_id": "non-existent-urr-id-12345",
                "password": "validpassword123",
                "username": "testuser"
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "Registration request not found" in response.json().get("detail", ""), \
            f"Expected registration request not found error, got: {response.json()}"
        print("✅ Test 2 passed: Invalid URR_ID returns proper error")

async def test_register_telegram_valid_request_structure():
    """Test that valid request structure is accepted (even if URR_ID doesn't exist)"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # This should pass validation but fail at URR_ID lookup (which is expected)
        response = await client.post(
            f"{API_BASE}/register-telegram",
            json={
                "urr_id": "test-valid-structure-123",
                "password": "validpassword123",
                "username": "testuser"
            }
        )
        # Should not be a 422 (validation error), but 400 (business logic error)
        assert response.status_code != 422, "Should not be validation error"
        # Should be 400 (registration request not found) or 500 (if there's a server error)
        assert response.status_code in [400, 500], \
            f"Expected 400 or 500, got {response.status_code}: {response.json()}"
        print("✅ Test passed: Valid request structure accepted (failed at URR_ID lookup as expected)")

if __name__ == "__main__":
    print("Running register_telegram_user endpoint validation tests...")
    asyncio.run(test_register_telegram_password_validation())
    asyncio.run(test_register_telegram_missing_urr_id())
    asyncio.run(test_register_telegram_valid_request_structure())
    print("\n✅ All endpoint validation tests passed!")

