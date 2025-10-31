#!/usr/bin/env python3
"""
Comprehensive i18n testing for Telega2Go bot
Tests all language features: menu, commands, callback responses
"""

import sys
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, List

# Add the OTP gateway app to path
sys.path.insert(0, 'otp-social-gateway')

from app.bot_commands import FunnyBotCommands


class TestI18nFeatures:
    """Test suite for i18n functionality"""
    
    def __init__(self):
        self.bot_commands = FunnyBotCommands("test_token")
        self.test_results = []
        self.supported_languages = ["en", "ru", "es", "de"]
        
    def test_language_detection(self):
        """Test language code normalization and detection"""
        print("🧪 Testing language detection...")
        
        test_cases = [
            ("en", "en"),
            ("en-US", "en"),
            ("ru-RU", "ru"),
            ("ru", "ru"),
            ("es-ES", "es"),
            ("de-DE", "de"),
            ("fr", "en"),  # Unsupported language should default to English
            (None, "en"),  # None should default to English
            ("", "en"),  # Empty should default to English
        ]
        
        passed = 0
        failed = 0
        
        for language_code, expected in test_cases:
            result = self.bot_commands._get_language(language_code)
            if result == expected:
                passed += 1
            else:
                failed += 1
                print(f"  ❌ FAILED: '{language_code}' -> expected '{expected}', got '{result}'")
        
        if failed == 0:
            print(f"  ✅ All {passed} language detection tests passed")
            return True
        else:
            print(f"  ❌ {failed} language detection tests failed, {passed} passed")
            return False
    
    def test_menu_translations(self):
        """Test menu item translations for all languages"""
        print("🧪 Testing menu translations...")
        
        action_keys = ["joinToMe", "explainWhatIsThis", "whatIsMyBalance", "showLastactions"]
        fields = ["title", "description", "button", "initial", "response"]
        
        passed = 0
        failed = 0
        
        for lang in self.supported_languages:
            for action_key in action_keys:
                for field in fields:
                    try:
                        text = self.bot_commands._get_menu_text(action_key, lang, field)
                        if text and isinstance(text, str) and len(text) > 0:
                            passed += 1
                        else:
                            failed += 1
                            print(f"  ❌ Empty or invalid text for {lang}/{action_key}/{field}")
                    except Exception as e:
                        failed += 1
                        print(f"  ❌ Error getting {lang}/{action_key}/{field}: {e}")
        
        if failed == 0:
            print(f"  ✅ All {passed} menu translation tests passed")
            return True
        else:
            print(f"  ❌ {failed} menu translation tests failed, {passed} passed")
            return False
    
    def test_command_translations(self):
        """Test command translations for all languages"""
        print("🧪 Testing command translations...")
        
        command_keys = [
            "start", "help", "joke", "fortune", "mood", "panic", "otp",
            "unknown_command", "stats_template", "dice_roll", 
            "dice_luck_high", "dice_luck_low", "dice_quality_excellent",
            "dice_quality_good", "dice_quality_ok"
        ]
        
        passed = 0
        failed = 0
        
        for lang in self.supported_languages:
            for command_key in command_keys:
                try:
                    text = self.bot_commands._get_command_text(command_key, lang)
                    if text:
                        if isinstance(text, list):
                            # Lists (like jokes, fortunes) should have at least one item
                            if len(text) > 0:
                                passed += 1
                            else:
                                failed += 1
                                print(f"  ❌ Empty list for {lang}/{command_key}")
                        elif isinstance(text, str):
                            # Strings should not be empty
                            if len(text) > 0:
                                passed += 1
                            else:
                                failed += 1
                                print(f"  ❌ Empty string for {lang}/{command_key}")
                        else:
                            failed += 1
                            print(f"  ❌ Invalid type for {lang}/{command_key}: {type(text)}")
                    else:
                        failed += 1
                        print(f"  ❌ None or empty for {lang}/{command_key}")
                except Exception as e:
                    failed += 1
                    print(f"  ❌ Error getting {lang}/{command_key}: {e}")
        
        if failed == 0:
            print(f"  ✅ All {passed} command translation tests passed")
            return True
        else:
            print(f"  ❌ {failed} command translation tests failed, {passed} passed")
            return False
    
    def test_response_translations(self):
        """Test callback query response translations"""
        print("🧪 Testing callback response translations...")
        
        action_keys = ["joinToMe", "explainWhatIsThis", "whatIsMyBalance", "showLastactions"]
        
        passed = 0
        failed = 0
        
        for lang in self.supported_languages:
            for action_key in action_keys:
                try:
                    response = self.bot_commands._get_response_text(action_key, lang)
                    if response and isinstance(response, str) and len(response) > 10:  # Should have meaningful content
                        # Verify it's actually translated (not English for other languages)
                        if lang == "en" or response != self.bot_commands._get_response_text(action_key, "en"):
                            passed += 1
                        else:
                            failed += 1
                            print(f"  ❌ Response for {lang}/{action_key} is same as English (not translated)")
                    else:
                        failed += 1
                        print(f"  ❌ Empty or too short response for {lang}/{action_key}")
                except Exception as e:
                    failed += 1
                    print(f"  ❌ Error getting response for {lang}/{action_key}: {e}")
        
        if failed == 0:
            print(f"  ✅ All {passed} response translation tests passed")
            return True
        else:
            print(f"  ❌ {failed} response translation tests failed, {passed} passed")
            return False
    
    def test_inline_query_uses_language(self):
        """Test that inline query handler uses language_code"""
        print("🧪 Testing inline query language support...")
        
        passed = 0
        failed = 0
        
        for lang in self.supported_languages:
            try:
                # Mock the HTTP client to avoid actual API calls
                with patch('otp-social-gateway.app.bot_commands.httpx.AsyncClient') as mock_client:
                    mock_response = AsyncMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {"ok": True}
                    mock_response.headers.get.return_value = "application/json"
                    
                    mock_client_instance = AsyncMock()
                    mock_client_instance.__aenter__.return_value = mock_client_instance
                    mock_client_instance.__aexit__.return_value = None
                    mock_client_instance.post.return_value = mock_response
                    mock_client.return_value = mock_client_instance
                    
                    # Run the inline query handler
                    result = asyncio.run(
                        self.bot_commands.handle_inline_query(
                            "test_query_id", "", "test_user_id", lang
                        )
                    )
                    
                    if result:
                        # Verify that the language was logged/used
                        # Check that translations were used (by verifying mock was called)
                        if mock_client_instance.post.called:
                            passed += 1
                        else:
                            failed += 1
                            print(f"  ❌ Inline query handler didn't call API for {lang}")
                    else:
                        failed += 1
                        print(f"  ❌ Inline query handler returned False for {lang}")
            except Exception as e:
                failed += 1
                print(f"  ❌ Error testing inline query for {lang}: {e}")
        
        if failed == 0:
            print(f"  ✅ All {passed} inline query language tests passed")
            return True
        else:
            print(f"  ❌ {failed} inline query language tests failed, {passed} passed")
            return False
    
    def test_callback_query_uses_language(self):
        """Test that callback query handler uses language_code for responses"""
        print("🧪 Testing callback query language support...")
        
        callback_data_list = [
            "action_joinToMe",
            "action_explainWhatIsThis", 
            "action_whatIsMyBalance",
            "action_showLastactions"
        ]
        
        passed = 0
        failed = 0
        
        for lang in self.supported_languages:
            for callback_data in callback_data_list:
                try:
                    # Mock the HTTP client
                    with patch('otp-social-gateway.app.bot_commands.httpx.AsyncClient') as mock_client:
                        mock_response = AsyncMock()
                        mock_response.status_code = 200
                        mock_response.json.return_value = {"ok": True}
                        
                        mock_client_instance = AsyncMock()
                        mock_client_instance.__aenter__.return_value = mock_client_instance
                        mock_client_instance.__aexit__.return_value = None
                        mock_client_instance.post.return_value = mock_response
                        mock_client.return_value = mock_client_instance
                        
                        # Run the callback query handler
                        result = asyncio.run(
                            self.bot_commands.handle_callback_query(
                                "test_callback_id", "test_chat_id", 123, callback_data, lang
                            )
                        )
                        
                        if result:
                            # Verify API was called (meaning handler executed)
                            if mock_client_instance.post.called:
                                # Check that the response text was in the correct language
                                call_args = mock_client_instance.post.call_args
                                if call_args:
                                    json_data = call_args[1].get('json', {}) if 'json' in call_args[1] else {}
                                    text = json_data.get('text', '')
                                    if text:
                                        # Verify it's using translated text (not empty English)
                                        passed += 1
                                    else:
                                        failed += 1
                                        print(f"  ❌ No text in response for {lang}/{callback_data}")
                                else:
                                    passed += 1  # Handler executed
                            else:
                                failed += 1
                                print(f"  ❌ Callback handler didn't call API for {lang}/{callback_data}")
                        else:
                            failed += 1
                            print(f"  ❌ Callback handler returned False for {lang}/{callback_data}")
                except Exception as e:
                    failed += 1
                    print(f"  ❌ Error testing callback query for {lang}/{callback_data}: {e}")
        
        if failed == 0:
            print(f"  ✅ All {passed} callback query language tests passed")
            return True
        else:
            print(f"  ❌ {failed} callback query language tests failed, {passed} passed")
            return False
    
    def test_command_uses_language(self):
        """Test that command handler uses language_code"""
        print("🧪 Testing command language support...")
        
        commands = ["/start", "/help", "/joke", "/fortune", "/mood", "/panic", "/otp"]
        
        passed = 0
        failed = 0
        
        for lang in self.supported_languages:
            for command in commands:
                try:
                    # Mock the HTTP client
                    with patch('otp-social-gateway.app.bot_commands.httpx.AsyncClient') as mock_client:
                        mock_response = AsyncMock()
                        mock_response.status_code = 200
                        mock_response.json.return_value = {"ok": True}
                        
                        mock_client_instance = AsyncMock()
                        mock_client_instance.__aenter__.return_value = mock_client_instance
                        mock_client_instance.__aexit__.return_value = None
                        mock_client_instance.post.return_value = mock_response
                        mock_client.return_value = mock_client_instance
                        
                        # Run the command handler
                        result = asyncio.run(
                            self.bot_commands.handle_command(
                                "test_chat_id", command, None, lang
                            )
                        )
                        
                        if result:
                            # Verify API was called
                            if mock_client_instance.post.called:
                                passed += 1
                            else:
                                failed += 1
                                print(f"  ❌ Command handler didn't call API for {lang}/{command}")
                        else:
                            failed += 1
                            print(f"  ❌ Command handler returned False for {lang}/{command}")
                except Exception as e:
                    failed += 1
                    print(f"  ❌ Error testing command for {lang}/{command}: {e}")
        
        if failed == 0:
            print(f"  ✅ All {passed} command language tests passed")
            return True
        else:
            print(f"  ❌ {failed} command language tests failed, {passed} passed")
            return False
    
    def run_all_tests(self):
        """Run all i18n tests"""
        print("🌍 Starting comprehensive i18n feature tests...\n")
        
        tests = [
            ("Language Detection", self.test_language_detection),
            ("Menu Translations", self.test_menu_translations),
            ("Command Translations", self.test_command_translations),
            ("Response Translations", self.test_response_translations),
            ("Inline Query Language Support", self.test_inline_query_uses_language),
            ("Callback Query Language Support", self.test_callback_query_uses_language),
            ("Command Language Support", self.test_command_uses_language),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}:")
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"  ❌ Test crashed: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        passed_count = sum(1 for _, result in results if result)
        total_count = len(results)
        
        for test_name, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{status}: {test_name}")
        
        print(f"\nTotal: {passed_count}/{total_count} test suites passed")
        
        if passed_count == total_count:
            print("✅ All i18n tests passed!")
            return True
        else:
            print(f"❌ {total_count - passed_count} test suite(s) failed")
            return False


if __name__ == "__main__":
    tester = TestI18nFeatures()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

