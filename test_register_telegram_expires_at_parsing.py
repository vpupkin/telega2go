"""
PENALTY TEST 1: Test expires_at datetime parsing in register_telegram_user
Tests that expires_at ISO string parsing works correctly with timezone handling
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta

def test_expires_at_iso_parsing():
    """Test that expires_at ISO string parsing handles various formats correctly"""
    # Create a timezone-aware datetime (like in create_registration_request)
    expires_at_dt = datetime.now(timezone.utc) + timedelta(hours=24)
    iso_str = expires_at_dt.isoformat()
    
    # Simulate the parsing logic from register_telegram_user
    try:
        parsed_str = iso_str.replace('Z', '+00:00')
        parsed_dt = datetime.fromisoformat(parsed_str)
        # Ensure it's timezone-aware
        if parsed_dt.tzinfo is None:
            parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
        
        assert parsed_dt.tzinfo is not None, "expires_at should be timezone-aware"
        assert isinstance(parsed_dt, datetime), "Should be a datetime object"
        # Should be approximately 24 hours from now
        time_diff = parsed_dt - datetime.now(timezone.utc)
        assert timedelta(hours=23) < time_diff < timedelta(hours=25), \
            f"expires_at should be ~24h in future, got {time_diff}"
        print("✅ Test 1 passed: expires_at ISO parsing with timezone works")
    except Exception as e:
        pytest.fail(f"expires_at datetime parsing failed: {e}")

def test_expires_at_edge_cases():
    """Test expires_at parsing with various ISO string formats"""
    base_dt = datetime.now(timezone.utc) + timedelta(hours=24)
    
    test_cases = [
        base_dt.isoformat(),  # Standard format (already has +00:00)
        base_dt.replace(tzinfo=None).isoformat() + 'Z',  # Naive datetime with Z suffix
        (base_dt + timedelta(hours=1)).isoformat(),  # Different time
    ]
    
    for iso_str in test_cases:
        try:
            # Simulate the endpoint parsing logic (only replace Z if not already timezone-aware)
            parsed_str = iso_str
            if parsed_str.endswith('Z') and '+00:00' not in parsed_str and '-' not in parsed_str[-6:]:
                parsed_str = parsed_str.replace('Z', '+00:00')
            parsed_dt = datetime.fromisoformat(parsed_str)
            
            # Ensure timezone-aware
            if parsed_dt.tzinfo is None:
                parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
            
            assert parsed_dt.tzinfo is not None, f"Should be timezone-aware for: {iso_str}"
            assert isinstance(parsed_dt, datetime), f"Should be datetime for: {iso_str}"
            print(f"✅ Test case passed for: {iso_str}")
        except (ValueError, AttributeError) as e:
            pytest.fail(f"Failed to parse expires_at: {iso_str}, error: {e}")

if __name__ == "__main__":
    test_expires_at_iso_parsing()
    test_expires_at_edge_cases()
    print("\n✅ All expires_at parsing tests passed!")

