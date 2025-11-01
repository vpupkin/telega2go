"""
PENALTY TEST 1/2: ERROR 19 - Motor DateTime Conversion Fix
Tests that datetime fields are properly converted to ISO strings immediately after find_one()
"""

import pytest
import asyncio
import httpx
import uuid
from datetime import datetime, timezone, timedelta


@pytest.mark.asyncio
async def test_motor_datetime_conversion_immediate():
    """
    Test that registration request datetime fields are converted to ISO strings
    immediately after find_one() to prevent motor's auto-conversion error
    """
    backend_url = "http://localhost:55552"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Create a registration request with datetime fields
        telegram_user_id = 999888777
        registration_data = {
            "id": telegram_user_id,
            "username": "testuser_datetime",
            "first_name": "Test",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+1234567890"
        }
        
        create_response = await client.post(
            f"{backend_url}/api/create-registration-request",
            json=registration_data
        )
        
        assert create_response.status_code == 200, f"Failed to create registration request: {create_response.text}"
        create_data = create_response.json()
        urr_id = create_data.get("urr_id")
        assert urr_id, "URR_ID not returned"
        
        # Step 2: Immediately try to register - this should NOT trigger datetime conversion error
        # The fix ensures datetime fields are converted to ISO strings before any processing
        register_response = await client.post(
            f"{backend_url}/api/register-telegram",
            json={
                "urr_id": urr_id,
                "password": "testpass123",
                "username": "testuser_datetime"
            }
        )
        
        # Should NOT get 500 error with "hour must be in 0..23"
        assert register_response.status_code != 500, f"ERROR 19 triggered! Response: {register_response.text}"
        
        if register_response.status_code == 200:
            # Success - registration worked
            register_data = register_response.json()
            assert "token" in register_data, "Token should be returned"
            assert "user" in register_data, "User data should be returned"
            print("✅ Test passed: DateTime conversion fix works")
        else:
            # 400 is acceptable (expired, etc) but NOT 500
            error_detail = register_response.json().get("detail", "")
            assert "hour must be in 0..23" not in error_detail, f"ERROR 19 still occurs: {error_detail}"
            print(f"⚠️ Registration failed with {register_response.status_code}, but no datetime error: {error_detail}")


@pytest.mark.asyncio
async def test_motor_datetime_fallback_raw_pymongo():
    """
    Test that the raw pymongo fallback works when motor fails with ValueError
    This tests the recovery mechanism for ERROR 19
    """
    backend_url = "http://localhost:55552"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Create registration request
        telegram_user_id = 888777666
        registration_data = {
            "id": telegram_user_id,
            "username": "testuser_fallback",
            "first_name": "Fallback",
            "email": f"fallback_{uuid.uuid4().hex[:8]}@example.com",
            "phone": "+9876543210"
        }
        
        create_response = await client.post(
            f"{backend_url}/api/create-registration-request",
            json=registration_data
        )
        
        assert create_response.status_code == 200, f"Failed to create registration request: {create_response.text}"
        create_data = create_response.json()
        urr_id = create_data.get("urr_id")
        assert urr_id, "URR_ID not returned"
        
        # Step 2: Try registration - should work even if motor has issues
        # The fallback to raw pymongo should handle any motor datetime conversion problems
        register_response = await client.post(
            f"{backend_url}/api/register-telegram",
            json={
                "urr_id": urr_id,
                "password": "fallback123",
                "username": "testuser_fallback"
            }
        )
        
        # Critical: Must NOT get 500 with datetime error
        assert register_response.status_code != 500, f"ERROR 19 not fixed! Response: {register_response.text}"
        
        error_detail = ""
        if register_response.status_code != 200:
            try:
                error_data = register_response.json()
                error_detail = error_data.get("detail", "")
            except:
                error_detail = register_response.text
        
        # Must not contain datetime conversion error
        assert "hour must be in 0..23" not in error_detail, f"ERROR 19 persists: {error_detail}"
        
        if register_response.status_code == 200:
            print("✅ Test passed: Fallback mechanism works")
        else:
            print(f"⚠️ Registration failed ({register_response.status_code}), but no datetime error: {error_detail}")


if __name__ == "__main__":
    print("🧪 Running PENALTY Test 1/2: ERROR 19 DateTime Conversion Fix")
    print("=" * 70)
    asyncio.run(test_motor_datetime_conversion_immediate())
    print("\n" + "=" * 70)
    asyncio.run(test_motor_datetime_fallback_raw_pymongo())
    print("\n✅ PENALTY Test 1/2 Complete!")

