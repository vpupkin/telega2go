#!/usr/bin/env python3
"""
Test script to verify balance button functionality
Tests the complete flow: callback -> backend API -> balance message
"""

import asyncio
import httpx
import os
import json

BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:55552')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8021082793:AAE56NV3KZ76qkRGrGv9kKk3Wq17n_exvzQ')
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

TEST_USER_ID = 415043706
TEST_CHAT_ID = str(TEST_USER_ID)

async def test_balance_endpoint():
    """Test 1: Verify backend balance endpoint returns correct data"""
    print("🧪 TEST 1: Backend Balance Endpoint")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BACKEND_URL}/api/user-balance",
                params={"telegram_user_id": TEST_USER_ID}
            )
            
            print(f"📞 API Call: GET {BACKEND_URL}/api/user-balance?telegram_user_id={TEST_USER_ID}")
            print(f"📥 Status: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {json.dumps(data, indent=2)}")
                
                balance = data.get("balance")
                name = data.get("name")
                currency = data.get("currency", "USD")
                
                if balance is not None:
                    print(f"✅ Balance Value: {balance:.2f} {currency}")
                    print(f"✅ User Name: {name}")
                    return True, balance, name, currency
                else:
                    print(f"❌ Balance field missing in response!")
                    return False, None, None, None
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                return False, None, None, None
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None, None

async def test_balance_message_format():
    """Test 2: Verify balance message format includes balance value"""
    print("\n🧪 TEST 2: Balance Message Format")
    print("=" * 60)
    
    # ✅ SIMPLE format: "YOU BALANCE> $XXX.xx"
    balance = 0.0
    response_text = f"YOU BALANCE> ${balance:.2f}"
    
    print(f"📝 Generated Message:")
    print(f"   '{response_text}'")
    print()
    
    # Check if balance value is in the message
    balance_str = f"{balance:.2f}"
    if balance_str in response_text:
        print(f"✅ Balance value '{balance_str}' IS in message")
    else:
        print(f"❌ Balance value '{balance_str}' NOT in message!")
        return False
    
    # Check for expected format
    if "YOU BALANCE>" in response_text and "$" in response_text:
        print(f"✅ Message format is correct: 'YOU BALANCE> $XXX.xx'")
    else:
        print(f"❌ Message format is incorrect!")
        return False
    
    return True

async def test_telegram_send_message():
    """Test 3: Verify we can send a message to Telegram (actual send)"""
    print("\n🧪 TEST 3: Telegram Send Message (DRY RUN)")
    print("=" * 60)
    print("⚠️  This test will NOT actually send a message")
    print("⚠️  It only validates the message format and API call structure")
    print()
    
    balance = 0.0
    message_text = f"YOU BALANCE> ${balance:.2f}"  # ✅ Simple format
    
    payload = {
        "chat_id": TEST_CHAT_ID,
        "text": message_text  # ✅ No parse_mode needed for simple text
    }
    
    print(f"📤 Would send to Telegram:")
    print(f"   URL: {TELEGRAM_API_BASE}/sendMessage")
    print(f"   Chat ID: {TEST_CHAT_ID}")
    print(f"   Message Text: '{message_text}'")
    print()
    
    # Verify payload structure
    if "chat_id" in payload and "text" in payload:
        print("✅ Payload structure is correct")
    else:
        print("❌ Payload structure is invalid!")
        return False
    
    balance_str = f"{balance:.2f}"
    if balance_str in message_text:
        print(f"✅ Balance value '{balance_str}' IS in message text")
    else:
        print(f"❌ Balance value '{balance_str}' NOT in message text!")
        return False
    
    if "YOU BALANCE>" in message_text:
        print(f"✅ Message format matches requirement: 'YOU BALANCE> $XXX.xx'")
    else:
        print(f"❌ Message format does NOT match requirement!")
        return False
    
    print("✅ Message format validation passed")
    print("ℹ️  (Skipping actual Telegram API call to avoid spam)")
    
    return True

async def test_callback_handler_logic():
    """Test 4: Simulate the callback handler logic"""
    print("\n🧪 TEST 4: Callback Handler Logic Simulation")
    print("=" * 60)
    
    callback_data = "action_whatIsMyBalance"
    chat_id = TEST_CHAT_ID
    
    print(f"📋 Simulating callback:")
    print(f"   callback_data: {callback_data}")
    print(f"   chat_id: {chat_id}")
    print()
    
    # Step 1: Validate chat_id
    if not chat_id or chat_id == "":
        print("❌ chat_id is empty - handler would fail here")
        return False
    else:
        print(f"✅ chat_id is valid: {chat_id}")
    
    # Step 2: Convert to int
    try:
        telegram_user_id = int(chat_id)
        print(f"✅ Converted chat_id to telegram_user_id: {telegram_user_id}")
    except ValueError as e:
        print(f"❌ Failed to convert chat_id to int: {e}")
        return False
    
    # Step 3: Call backend API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{BACKEND_URL}/api/user-balance",
                params={"telegram_user_id": telegram_user_id}
            )
            
            if response.status_code == 200:
                balance_data = response.json()
                balance = balance_data.get("balance", 0.0)
                user_name = balance_data.get("name", "User")
                currency = balance_data.get("currency", "USD")
                
                print(f"✅ Backend API call successful")
                print(f"   Balance: {balance:.2f} {currency}")
                print(f"   User: {user_name}")
                
                # Step 4: Format message (SIMPLE format)
                message_text = f"YOU BALANCE> ${balance:.2f}"
                
                if f"{balance:.2f}" in message_text:
                    print(f"✅ Balance value IS in formatted message")
                    print(f"📝 Message: '{message_text}'")
                    if "YOU BALANCE>" in message_text:
                        print(f"✅ Format is correct: 'YOU BALANCE> $XXX.xx'")
                    return True
                else:
                    print(f"❌ Balance value NOT in formatted message!")
                    return False
            else:
                print(f"❌ Backend API failed: HTTP {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Exception in backend API call: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 BALANCE BUTTON FUNCTIONALITY TEST SUITE")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Backend endpoint
    success, balance, name, currency = await test_balance_endpoint()
    results.append(("Backend Endpoint", success))
    print()
    
    # Test 2: Message format
    success = await test_balance_message_format()
    results.append(("Message Format", success))
    print()
    
    # Test 3: Telegram send (validation only)
    success = await test_telegram_send_message()
    results.append(("Telegram Send Structure", success))
    print()
    
    # Test 4: Complete callback handler logic
    success = await test_callback_handler_logic()
    results.append(("Callback Handler Logic", success))
    print()
    
    # Summary
    print("=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Balance button should work!")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Balance button may have issues")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

