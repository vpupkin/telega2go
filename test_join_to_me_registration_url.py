#!/usr/bin/env python3
"""
PENALTY ROUND: Tests for Join To Me Registration URL Button
TDD: Two tests for the registration URL button in Join To Me action
"""

import pytest
import sys
from unittest.mock import AsyncMock, Mock, patch
import json

sys.path.insert(0, 'otp-social-gateway')


class TestJoinToMeRegistrationURL:
    """PENALTY ROUND: Tests for Join To Me registration URL button"""
    
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
    
    # TEST 1: Join To Me inline query result MUST include registration URL button
    async def test_join_to_me_has_registration_url_button(self, sample_unregistered_user_data, mock_telegram_service):
        """PENALTY TEST 1: Join To Me inline query must include registration URL button"""
        # Arrange
        from otp_social_gateway.app.bot_commands import FunnyBotCommands
        
        bot = FunnyBotCommands("fake_token")
        inline_query_id = "test_query_123"
        telegram_user_id = sample_unregistered_user_data["id"]
        
        # Act
        # We need to mock the Telegram API call and capture the results
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
            assert call_args is not None
            
            # Extract results from the JSON
            json_data = call_args.kwargs.get("json", {})
            results = json_data.get("results", [])
            
            # Find Join To Me result
            join_to_me_result = None
            for result in results:
                if result.get("title", "").startswith("👥"):
                    join_to_me_result = result
                    break
            
            assert join_to_me_result is not None, "Join To Me result not found"
            
            # ✅ CRITICAL: Check for URL button in reply_markup
            reply_markup = join_to_me_result.get("reply_markup", {})
            inline_keyboard = reply_markup.get("inline_keyboard", [])
            assert len(inline_keyboard) > 0, "No inline keyboard found"
            
            button = inline_keyboard[0][0]
            assert "url" in button, "Button must have 'url' field for Join To Me"
            assert button["url"].startswith("https://putana.date/registrationOfNewUser"), \
                f"Registration URL incorrect: {button.get('url')}"
            assert f"telegram_user_id={telegram_user_id}" in button["url"], \
                "Registration URL must include telegram_user_id"
            
            print("✅ PENALTY TEST 1 PASSED: Join To Me has registration URL button")
            print(f"   URL: {button['url']}")
    
    # TEST 2: Registration URL button must work correctly for different telegram_user_ids
    async def test_join_to_me_url_includes_correct_telegram_user_id(self, mock_telegram_service):
        """PENALTY TEST 2: Registration URL must include correct telegram_user_id"""
        # Arrange
        from otp_social_gateway.app.bot_commands import FunnyBotCommands
        
        bot = FunnyBotCommands("fake_token")
        inline_query_id = "test_query_456"
        
        # Test with different user IDs
        test_cases = [
            123456789,
            987654321,
            555666777
        ]
        
        for telegram_user_id in test_cases:
            user_data = {
                "id": telegram_user_id,
                "first_name": "Test",
                "language_code": "en"
            }
            
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
                    full_user_data=user_data,
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
                
                button = join_to_me_result["reply_markup"]["inline_keyboard"][0][0]
                assert "url" in button
                assert f"telegram_user_id={telegram_user_id}" in button["url"], \
                    f"URL must include correct telegram_user_id={telegram_user_id}, got: {button['url']}"
                
                print(f"✅ Test passed for telegram_user_id={telegram_user_id}")
                print(f"   URL: {button['url']}")
        
        print("✅ PENALTY TEST 2 PASSED: Registration URL includes correct telegram_user_id for all test cases")


if __name__ == "__main__":
    print("🚨 PENALTY ROUND: Tests for Join To Me Registration URL Button")
    print("=" * 60)
    print("\nThese tests verify the registration URL button is present.")
    print("Run with: pytest test_join_to_me_registration_url.py -v")
    print("\n" + "=" * 60)

