#!/usr/bin/env python3
"""
PENALTY++ ROUND: Tests for Join To Me Callback Handler
TDD: Two tests to verify callback handler sends registration URL
"""

import pytest
import sys
from unittest.mock import AsyncMock, Mock, patch

sys.path.insert(0, 'otp-social-gateway')


class TestJoinToMeCallbackHandler:
    """PENALTY++: Tests for Join To Me callback query handler"""
    
    @pytest.fixture
    def mock_telegram_service(self):
        """Mock TelegramUserService"""
        service = Mock()
        service.check_registration_status = AsyncMock(return_value={
            "is_registered": False,
            "is_verified": False,
            "user": None
        })
        return service
    
    # TEST 1: Callback handler MUST send message with registration URL
    async def test_join_to_me_callback_sends_registration_url(self, mock_telegram_service):
        """PENALTY++ TEST 1: joinToMe callback must send message with clickable URL"""
        # Arrange
        from app.bot_commands import FunnyBotCommands
        
        bot = FunnyBotCommands("fake_token")
        callback_query_id = "callback_123"
        chat_id = "123456789"  # telegram_user_id
        callback_data = "action_joinToMe"
        
        # Act
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"ok": True}
            mock_post.return_value = mock_response
            
            success = await bot.handle_callback_query(
                callback_query_id,
                chat_id,
                0,  # message_id
                callback_data,
                "en",
                telegram_user_service=mock_telegram_service
            )
            
            # Assert
            assert success is True
            assert mock_post.called
            
            # Get all API calls
            calls = mock_post.call_args_list
            assert len(calls) >= 2, "Must call answerCallbackQuery and sendMessage"
            
            # Find sendMessage call
            send_message_call = None
            for call in calls:
                url = call.args[0] if call.args else ""
                if "sendMessage" in url:
                    send_message_call = call
                    break
            
            assert send_message_call is not None, "sendMessage must be called"
            
            # Extract message content
            json_data = send_message_call.kwargs.get("json", {})
            message_text = json_data.get("text", "")
            
            # ✅ CRITICAL: Message must contain clickable URL
            assert "registrationOfNewUser" in message_text, "Message must contain registration URL"
            assert f"telegram_user_id={chat_id}" in message_text, "Message must include telegram_user_id"
            assert "<a href=" in message_text, "Message must contain HTML link"
            assert "Click here to start registration" in message_text, "Message must have registration link text"
            
            # Verify parse_mode is HTML
            assert json_data.get("parse_mode") == "HTML", "Must use HTML parse mode for clickable links"
            
            print("✅ PENALTY++ TEST 1 PASSED: Callback handler sends registration URL")
            print(f"   Message: {message_text[:100]}...")
    
    # TEST 2: Callback handler must generate correct URL with telegram_user_id
    async def test_join_to_me_callback_url_format(self, mock_telegram_service):
        """PENALTY++ TEST 2: Registration URL format must be correct"""
        # Arrange
        from app.bot_commands import FunnyBotCommands
        
        bot = FunnyBotCommands("fake_token")
        callback_query_id = "callback_456"
        
        # Test with different telegram_user_ids
        test_cases = [
            ("123456789", 123456789),
            ("987654321", 987654321),
            ("555666777", 555666777)
        ]
        
        for chat_id_str, telegram_user_id in test_cases:
            # Act
            with patch('httpx.AsyncClient.post') as mock_post:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"ok": True}
                mock_post.return_value = mock_response
                
                await bot.handle_callback_query(
                    callback_query_id,
                    chat_id_str,
                    0,
                    "action_joinToMe",
                    "en",
                    telegram_user_service=mock_telegram_service
                )
                
                # Assert
                # Find sendMessage call
                send_message_call = None
                for call in mock_post.call_args_list:
                    url = call.args[0] if call.args else ""
                    if "sendMessage" in url:
                        send_message_call = call
                        break
                
                assert send_message_call is not None
                
                json_data = send_message_call.kwargs.get("json", {})
                message_text = json_data.get("text", "")
                
                # ✅ CRITICAL: URL must be correct format
                expected_url = f"https://putana.date/registrationOfNewUser?telegram_user_id={telegram_user_id}"
                assert expected_url in message_text, \
                    f"URL must be {expected_url}, got: {message_text}"
                
                # Verify HTML link format
                assert f"<a href='{expected_url}'>" in message_text, "HTML link format must be correct"
                
                print(f"✅ Test passed for telegram_user_id={telegram_user_id}")
                print(f"   URL: {expected_url}")
        
        print("✅ PENALTY++ TEST 2 PASSED: Registration URL format is correct for all test cases")


if __name__ == "__main__":
    print("🚨 PENALTY++ ROUND: Tests for Join To Me Callback Handler")
    print("=" * 60)
    print("\nThese tests verify callback handler sends registration URL.")
    print("Run with: pytest test_join_to_me_callback_handler.py -v")
    print("\n" + "=" * 60)

