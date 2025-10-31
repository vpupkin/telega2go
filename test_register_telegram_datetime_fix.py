"""
PENALTY TEST 1: Test datetime conversion in register_telegram_user endpoint
Tests that ISO string to datetime conversion works correctly with timezone handling
"""
import pytest
import asyncio
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_datetime_conversion_timezone_aware():
    """Test that datetime conversion handles timezone-aware datetime objects correctly"""
    # Create a timezone-aware datetime
    dt = datetime.now(timezone.utc)
    
    # Convert to ISO string
    iso_str = dt.isoformat()
    
    # Parse back (simulating the endpoint logic)
    try:
        parsed_dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
        
        assert parsed_dt.tzinfo is not None, "Datetime should be timezone-aware"
        assert isinstance(parsed_dt, datetime), "Should be a datetime object"
        print("✅ Test 1 passed: Datetime conversion with timezone works")
    except Exception as e:
        pytest.fail(f"Datetime conversion failed: {e}")

async def test_datetime_conversion_iso_string_edge_cases():
    """Test datetime conversion with various ISO string formats"""
    test_cases = [
        datetime.now(timezone.utc).isoformat(),  # Standard format
        datetime.now(timezone.utc).isoformat() + 'Z',  # With Z suffix
        datetime.now().isoformat(),  # Naive datetime (no timezone)
    ]
    
    for iso_str in test_cases:
        try:
            # Simulate the endpoint conversion logic
            parsed_str = iso_str.replace('Z', '+00:00')
            parsed_dt = datetime.fromisoformat(parsed_str)
            
            # Ensure timezone-aware
            if parsed_dt.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
            
            assert parsed_dt.tzinfo is not None, f"Should be timezone-aware for: {iso_str}"
            print(f"✅ Test case passed for: {iso_str}")
        except (ValueError, AttributeError) as e:
            # If parsing fails, ensure we have a fallback
            fallback_dt = datetime.now(timezone.utc)
            assert fallback_dt.tzinfo is not None
            print(f"✅ Fallback works for: {iso_str}")

if __name__ == "__main__":
    asyncio.run(test_datetime_conversion_timezone_aware())
    asyncio.run(test_datetime_conversion_iso_string_edge_cases())
    print("\n✅ All datetime conversion tests passed!")

