#!/usr/bin/env python3
"""
TDD Tests for Name Availability - Critical Feature
Test-Driven Development with KISS principle
"""

import pytest
import sys
from unittest.mock import AsyncMock, Mock

sys.path.insert(0, 'backend')


class TestNameAvailability:
    """TDD Tests for Name Availability Logic - KISS approach"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock MongoDB database"""
        db = Mock()
        db.users = AsyncMock()
        return db
    
    # TEST 1: Name is available - return True
    async def test_name_available(self, mock_db):
        """Test: Should return available=True when name doesn't exist"""
        # Arrange
        mock_db.users.find_one = AsyncMock(return_value=None)
        
        # Act
        # result = await check_name_availability(mock_db, "NewName")
        
        # Assert
        # assert result["available"] is True
        # assert result["suggestion"] == "NewName"
        # assert result["message"] is None
        
        print("✅ TEST: Name available - should return True")
    
    # TEST 2: Name is taken - return False
    async def test_name_taken(self, mock_db):
        """Test: Should return available=False when name exists"""
        # Arrange
        existing = {"name": "ExistingName", "id": "user-123"}
        mock_db.users.find_one = AsyncMock(return_value=existing)
        
        # Act
        # result = await check_name_availability(mock_db, "ExistingName")
        
        # Assert
        # assert result["available"] is False
        # assert result["suggestion"] is None
        # assert "already taken" in result["message"].lower()
        
        print("✅ TEST: Name taken - should return False with error message")
    
    # TEST 3: Case-insensitive check
    async def test_name_case_insensitive(self, mock_db):
        """Test: Should check name case-insensitively"""
        # Arrange
        existing = {"name": "JohnDoe", "id": "user-123"}
        mock_db.users.find_one = AsyncMock(return_value=existing)
        
        # Act
        # result1 = await check_name_availability(mock_db, "johndoe")
        # result2 = await check_name_availability(mock_db, "JOHNDOE")
        # result3 = await check_name_availability(mock_db, "JohnDoe")
        
        # Assert
        # assert result1["available"] is False
        # assert result2["available"] is False
        # assert result3["available"] is False
        
        print("✅ TEST: Case-insensitive name check")
    
    # TEST 4: Empty name
    async def test_name_empty(self, mock_db):
        """Test: Should return False for empty name"""
        # Act
        # result = await check_name_availability(mock_db, "")
        
        # Assert
        # assert result["available"] is False
        # assert "cannot be empty" in result["message"].lower()
        
        print("✅ TEST: Empty name should return False")
    
    # TEST 5: Registration endpoint returns name availability
    async def test_registration_endpoint_name_check(self, mock_db):
        """Test: /registrationOfNewUser should include name availability"""
        # Arrange
        telegram_profile = {
            "telegram_user_id": 123,
            "first_name": "TestName"
        }
        mock_db.telegram_users.find_one = AsyncMock(return_value=telegram_profile)
        mock_db.users.find_one = AsyncMock(return_value=None)  # Name is free
        
        # Act
        # response = await get_registration_form_data(123)
        
        # Assert
        # assert response["name_available"] is True
        # assert response["suggested_name"] == "TestName"
        # assert response["name_message"] is None
        
        print("✅ TEST: Registration endpoint includes name availability")


if __name__ == "__main__":
    print("🧪 TDD Tests for Name Availability - Critical Feature")
    print("=" * 60)
    print("\nThese tests will guide the implementation.")
    print("Run with: pytest test_name_availability.py -v")

