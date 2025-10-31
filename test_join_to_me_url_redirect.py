#!/usr/bin/env python3
"""
PENALTY++ ROUND: Tests for Join To Me URL Redirect Functionality
TDD: Two tests to verify URL redirect works correctly
"""

import pytest
import sys
from unittest.mock import AsyncMock, Mock, patch
import json

sys.path.insert(0, 'otp-social-gateway')


class TestJoinToMeURLRedirect:
    """PENALTY++: Tests for Join To Me URL redirect functionality"""
    
    @pytest.fixture
    def sample_unregistered_user_data(self):
        """Sample Telegram user data for unregistered user"""
        return {
            "id": 123456789,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "language_code": "en"
        }
    
    @pytest.fixture
    def mock_telegram_service(self):
        """Mock TelegramUserService"""
        service = Mock()
        service.check_registration_status = AsyncMock(return_value={
            "is_registered": False,
            "is_verified": False,
            "user": None
        })
        service.save_telegram_profile = AsyncMock()
        return service
    
    # TEST 1: Message content MUST include clickable URL link
    async def test_join_to_me_message_has_clickable_url(self, sample_unregistered_user_data, mock_telegram_service):
        """PENALTY++ TEST 1: Join To Me message must include clickable URL in message content"""
        # Arrange
        from app.bot_commands import FunnyBotCommands
        
        bot = FunnyBotCommands("fake_token")
        inline_query_id = "test_query_789"
        telegram_user_id = sample_unregistered_user_data["id"]
        
        # Act
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_post.return_value = mock_response
            
            success = await bot.handle_inline_query(
                inline_query_id,
                "",
                str(telegram_user_id),
                "en",
                full_user_data=sample_unregistered_user_data,
                telegram_user_service=mock_telegram_service
            )
            
            # Assert
            assert success is True
            assert mock_post.called
            
            # Get the call arguments
            call_args = mock_post.call_args
            json_data = call_args.kwargs.get("json", {})
            results = json_data.get("results", [])
            
            # Find Join To Me result
            join_to_me_result = None
            for result in results:
                if result.get("title", "").startswith("👥"):
                    join_to_me_result = result
                    break
            
            assert join_to_me_result is not None, "Join To Me result not found"
            
            # ✅ CRITICAL: Check message content has clickable URL
            message_content = join_to_me_result.get("input_message_content", {})
            message_text = message_content.get("message_text", "")
            
            assert "<a href=" in message_text, "Message must contain clickable URL link"
            assert "registrationOfNewUser" in message_text, "Message must contain registration URL"
            assert f"telegram_user_id={telegram_user_id}" in message_text, "Message must include telegram_user_id"
            
            # Verify URL format is correct HTML link
            assert "https://putana.date/registrationOfNewUser" in message_text
            assert "Click here to start registration" in message_text or "start registration" in message_text.lower()
            
            print("✅ PENALTY++ TEST 1 PASSED: Message content has clickable URL")
            print(f"   Message contains: {message_text[:100]}...")
    
    # TEST 2: Both button URL and message link must have same registration URL
    async def test_join_to_me_button_and_message_url_match(self, sample_unregistered_user_data, mock_telegram_service):
        """PENALTY++ TEST 2: Button URL and message link must match and be valid"""
        # Arrange
        from app.bot_commands import FunnyBotCommands
        
        bot = FunnyBotCommands("fake_token")
        inline_query_id = "test_query_999"
        telegram_user_id = sample_unregistered_user_data["id"]
        
        # Act
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_post.return_value = mock_response
            
            await bot.handle_inline_query(
                inline_query_id,
                "",
                str(telegram_user_id),
                "en",
                full_user_data=sample_unregistered_user_data,
                telegram_user_service=mock_telegram_service
            )
            
            # Assert
            call_args = mock_post.call_args
            json_data = call_args.kwargs.get("json", {})
            results = json_data.get("results", [])
            
            # Find Join To Me result
            join_to_me_result = None
            for result in results:
                if result.get("title", "").startswith("👥"):
                    join_to_me_result = result
                    break
            
            assert join_to_me_result is not None
            
            # Extract button URL
            button = join_to_me_result["reply_markup"]["inline_keyboard"][0][0]
            button_url = button.get("url", "")
            
            # Extract message link URL
            message_content = join_to_me_result.get("input_message_content", {})
            message_text = message_content.get("message_text", "")
            
            # Parse URL from HTML link
            import re
            url_match = re.search(r"href='([^']+)'", message_text)
            assert url_match is not None, "No URL found in message HTML link"
            message_url = url_match.group(1)
            
            # ✅ CRITICAL: Both URLs must match and include telegram_user_id
            assert button_url == message_url, f"Button URL and message URL must match. Button: {button_url}, Message: {message_url}"
            assert f"telegram_user_id={telegram_user_id}" in button_url
            assert f"telegram_user_id={telegram_user_id}" in message_url
            assert button_url.startswith("https://putana.date/registrationOfNewUser")
            assert message_url.startswith("https://putana.date/registrationOfNewUser")
            
            print("✅ PENALTY++ TEST 2 PASSED: Button and message URLs match")
            print(f"   Button URL: {button_url}")
            print(f"   Message URL: {message_url}")


if __name__ == "__main__":
    print("🚨 PENALTY++ ROUND: Tests for Join To Me URL Redirect")
    print("=" * 60)
    print("\nThese tests verify the URL redirect works correctly.")
    print("Run with: pytest test_join_to_me_url_redirect.py -v")
    print("\n" + "=" * 60)

