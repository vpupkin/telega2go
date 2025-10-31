#!/usr/bin/env python3
"""
Test script for Telegram inline query functionality
Tests the webhook endpoint with a simulated inline query
"""

import requests
import json
import sys

def test_inline_query():
    """Test inline query handling via webhook"""
    
    webhook_url = "http://localhost:55551/webhook"
    
    # Simulate an inline query update from Telegram
    test_update = {
        "update_id": 123456789,
        "inline_query": {
            "id": "test_inline_query_123",
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "query": "",
            "offset": ""
        }
    }
    
    print("🧪 Testing Inline Query Webhook")
    print("=" * 50)
    print(f"Webhook URL: {webhook_url}")
    print(f"Test Update: {json.dumps(test_update, indent=2)}")
    print()
    
    try:
        response = requests.post(
            webhook_url,
            json=test_update,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("\n✅ SUCCESS: Inline query handler responded correctly!")
                return True
            else:
                print(f"\n⚠️  WARNING: Handler returned: {data}")
                return False
        else:
            print(f"\n❌ ERROR: Webhook returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to webhook. Is OTP Gateway running?")
        print("   Check: docker ps | grep otp-gateway")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def test_webhook_info():
    """Check webhook configuration (requires bot token)"""
    
    # Get bot token from environment or docker-compose
    print("\n📋 Checking Webhook Configuration")
    print("=" * 50)
    print("To check webhook status, you need to run:")
    print()
    print("curl -X GET 'https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo'")
    print()
    print("Or check in BotFather:")
    print("/mybots → Select taxoin_bot → Bot Settings → Webhook")
    print()

def test_inline_mode():
    """Instructions for testing inline mode"""
    
    print("\n📱 Testing Inline Mode in Telegram")
    print("=" * 50)
    print("1. Open Telegram (any chat)")
    print("2. Type: @taxoin_bot")
    print("3. You should see a menu with 4 options")
    print()
    print("If menu doesn't appear:")
    print("  a) Enable inline mode: /setinline in BotFather")
    print("  b) Check webhook is configured")
    print("  c) Check bot is running and accessible")
    print()

if __name__ == "__main__":
    print("🚀 Telegram Inline Query Test Suite")
    print("=" * 50)
    print()
    
    # Test 1: Webhook endpoint
    webhook_ok = test_inline_query()
    
    # Test 2: Webhook info instructions
    test_webhook_info()
    
    # Test 3: Inline mode instructions
    test_inline_mode()
    
    print("\n" + "=" * 50)
    if webhook_ok:
        print("✅ Webhook endpoint is working!")
        print("   Next: Enable inline mode in BotFather and test in Telegram")
    else:
        print("❌ Webhook endpoint test failed")
        print("   Check OTP Gateway logs: docker logs telega2go-otp-gateway -f")
    
    sys.exit(0 if webhook_ok else 1)

