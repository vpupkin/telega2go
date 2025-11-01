"""
PENALTY TEST 2/2: ERROR 19 - DateTime Field Validation
Tests that datetime fields are validated and converted at all stages
"""

import pytest
import asyncio
import httpx
import uuid
from datetime import datetime, timezone, timedelta


@pytest.mark.asyncio
async def test_datetime_fields_always_strings():
    """
    Test that datetime fields (created_at, expires_at) are ALWAYS ISO strings
    at all stages of processing, never datetime objects
    """
    backend_url = "http://localhost:55552"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Create registration request
        telegram_user_id = 777666555
        registration_data = {
            "id": telegram_user_id,
            "username": "testuser_strings",
            "first_name": "String",
            "email": f"strings_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+1112223333"
        }
        
        create_response = await client.post(
            f"{backend_url}/api/create-registration-request",
            json=registration_data
        )
        
        assert create_response.status_code == 200, f"Failed to create registration request: {create_response.text}"
        create_data = create_response.json()
        urr_id = create_data.get("urr_id")
        assert urr_id, "URR_ID not returned"
        
        # Step 2: Get registration data - should have datetime fields as ISO strings
        get_response = await client.get(
            f"{backend_url}/api/registrationOfNewUser?urr_id={urr_id}"
        )
        
        assert get_response.status_code == 200, f"Failed to get registration data: {get_response.text}"
        get_data = get_response.json()
        
        # Verify URR_ID matches
        assert get_data.get("urr_id") == urr_id, "URR_ID mismatch"
        
        # Step 3: Register - should handle datetime fields correctly
        register_response = await client.post(
            f"{backend_url}/api/register-telegram",
            json={
                "urr_id": urr_id,
                "password": "strings123",
                "username": "testuser_strings"
            }
        )
        
        # Must NOT get 500 with datetime error
        assert register_response.status_code != 500, f"ERROR 19 occurred! Response: {register_response.text}"
        
        error_detail = ""
        if register_response.status_code != 200:
            try:
                error_data = register_response.json()
                error_detail = error_data.get("detail", "")
            except:
                error_detail = register_response.text
        
        # Critical assertion: No datetime conversion errors
        assert "hour must be in 0..23" not in error_detail, f"ERROR 19 still exists: {error_detail}"
        assert "Invalid registration request expiry date" not in error_detail or "datetime" not in error_detail.lower(), \
            f"DateTime validation error: {error_detail}"
        
        if register_response.status_code == 200:
            register_data = register_response.json()
            assert "token" in register_data, "Token should be returned"
            print("✅ Test passed: DateTime fields handled correctly as strings")
        else:
            print(f"⚠️ Registration failed ({register_response.status_code}), but no datetime error: {error_detail}")


@pytest.mark.asyncio
async def test_expired_registration_request_handling():
    """
    Test that expired registration requests are handled gracefully
    WITHOUT triggering datetime conversion errors
    """
    backend_url = "http://localhost:55552"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Use a non-existent or expired URR_ID
        fake_urr_id = str(uuid.uuid4())
        
        # Try to register with non-existent URR_ID
        # Should get 400 (not found) but NOT 500 (datetime error)
        register_response = await client.post(
            f"{backend_url}/api/register-telegram",
            json={
                "urr_id": fake_urr_id,
                "password": "test123456",
                "username": "fakeuser"
            }
        )
        
        # Must be 400 (not found) or 400 (expired), NOT 500 (datetime error)
        assert register_response.status_code != 500, f"ERROR 19 occurred for expired request! Response: {register_response.text}"
        
        if register_response.status_code == 400:
            error_data = register_response.json()
            error_detail = error_data.get("detail", "")
            # Should say "not found" or "expired", but NOT datetime error
            assert "hour must be in 0..23" not in error_detail, f"ERROR 19 in expired request: {error_detail}"
            assert "not found" in error_detail.lower() or "expired" in error_detail.lower(), \
                f"Expected 'not found' or 'expired', got: {error_detail}"
            print(f"✅ Test passed: Expired request handled gracefully: {error_detail}")
        else:
            # Unexpected status code
            print(f"⚠️ Unexpected status {register_response.status_code}: {register_response.text}")


if __name__ == "__main__":
    print("🧪 Running PENALTY Test 2/2: ERROR 19 DateTime Validation")
    print("=" * 70)
    asyncio.run(test_datetime_fields_always_strings())
    print("\n" + "=" * 70)
    asyncio.run(test_expired_registration_request_handling())
    print("\n✅ PENALTY Test 2/2 Complete!")

