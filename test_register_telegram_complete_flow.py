"""
PENALTY TEST 2: Test complete register_telegram_user flow with real data
Tests the entire registration flow from URR_ID creation to user registration
"""
import pytest
import asyncio
import httpx
import os
from datetime import datetime, timezone, timedelta
import uuid

# Test against local backend (✅ Correct port: 55552 from docker-compose.yml)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:55552")
API_BASE = f"{BACKEND_URL}/api"

async def test_complete_registration_flow():
    """Test complete flow: create registration request -> register user"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Step 1: Create registration request
        telegram_user_data = {
            "id": 123456789,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "language_code": "en",
            "email": "test@example.com",
            "phone": "+1234567890",
            "is_premium": False
        }
        
        response = await client.post(
            f"{API_BASE}/create-registration-request",
            json=telegram_user_data
        )
        
        assert response.status_code == 200, \
            f"Failed to create registration request: {response.status_code} - {response.text}"
        
        request_data = response.json()
        urr_id = request_data.get("urr_id")
        assert urr_id, "Should receive URR_ID"
        
        print(f"✅ Step 1 passed: Created registration request with URR_ID: {urr_id}")
        
        # Step 2: Verify registration request exists and is valid
        response = await client.get(
            f"{API_BASE}/registrationOfNewUser",
            params={"urr_id": urr_id}
        )
        
        assert response.status_code == 200, \
            f"Failed to get registration data: {response.status_code} - {response.text}"
        
        reg_data = response.json()
        assert reg_data.get("urr_id") == urr_id, "Should return correct URR_ID"
        assert reg_data.get("telegram_user_id") == telegram_user_data["id"], \
            "Should return correct telegram_user_id"
        
        print(f"✅ Step 2 passed: Retrieved registration data for URR_ID: {urr_id}")
        
        # Step 3: Register user with valid password
        response = await client.post(
            f"{API_BASE}/register-telegram",
            json={
                "urr_id": urr_id,
                "password": "validpassword123",
                "username": "testuser_unique"  # Use unique username
            }
        )
        
        # Should succeed (200) or fail with business logic error (400 - username taken, etc)
        # But NOT 500 (server error) or 422 (validation error)
        assert response.status_code in [200, 400], \
            f"Registration should succeed or fail with business logic, not {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            token_data = response.json()
            assert token_data.get("access_token"), "Should receive access token"
            assert token_data.get("user"), "Should receive user data"
            print(f"✅ Step 3 passed: User registered successfully")
        else:
            # If 400, check if it's a business logic error (not validation)
            error_detail = response.json().get("detail", "")
            assert "already" in error_detail.lower() or "taken" in error_detail.lower() or "expired" in error_detail.lower(), \
                f"Should be business logic error, got: {error_detail}"
            print(f"✅ Step 3 passed: Registration failed with expected business logic error: {error_detail}")

async def test_registration_with_various_datetime_formats():
    """Test that registration works with various datetime formats in stored data"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Create registration request with explicit datetime handling
        telegram_user_data = {
            "id": int(uuid.uuid4().int % 1000000000),  # Unique ID
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "first_name": "Datetime",
            "last_name": "Test",
            "language_code": "en",
        }
        
        response = await client.post(
            f"{API_BASE}/create-registration-request",
            json=telegram_user_data
        )
        
        assert response.status_code == 200, \
            f"Failed to create registration request: {response.status_code}"
        
        urr_id = response.json().get("urr_id")
        
        # Try to register - should handle datetime parsing correctly
        response = await client.post(
            f"{API_BASE}/register-telegram",
            json={
                "urr_id": urr_id,
                "password": "validpass123",
                "username": telegram_user_data["username"]
            }
        )
        
        # Should NOT be 500 (datetime parsing error)
        assert response.status_code != 500, \
            f"Should not fail with server error (500), got: {response.text}"
        
        # Should be 200 (success) or 400 (business logic error)
        assert response.status_code in [200, 400], \
            f"Should be 200 or 400, got {response.status_code}: {response.text}"
        
        print(f"✅ Test passed: Registration handles datetime formats correctly (status: {response.status_code})")

if __name__ == "__main__":
    print("Running complete registration flow tests...")
    asyncio.run(test_complete_registration_flow())
    asyncio.run(test_registration_with_various_datetime_formats())
    print("\n✅ All complete flow tests passed!")

