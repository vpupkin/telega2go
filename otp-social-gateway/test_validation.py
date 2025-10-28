#!/usr/bin/env python3
"""Quick validation test for OTP Gateway structure"""

import sys
import json

def test_imports():
    """Test all imports work"""
    try:
        from app.config import settings
        from app.models import SendOTPRequest, SendOTPResponse, ErrorResponse
        from app.otp_service import OTPService
        from app.main import app
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_pydantic_models():
    """Test Pydantic validation"""
    try:
        from app.models import SendOTPRequest
        
        # Test valid request
        valid = SendOTPRequest(
            chat_id="123456789",
            otp="483920",
            expire_seconds=30
        )
        print(f"✅ Valid request model: {valid.chat_id}, OTP: {valid.otp}")
        
        # Test validation - invalid OTP
        try:
            invalid = SendOTPRequest(
                chat_id="123",
                otp="12",  # Too short
                expire_seconds=30
            )
            print("❌ Should have failed validation for short OTP")
            return False
        except Exception as e:
            print(f"✅ Validation working: {type(e).__name__}")
        
        return True
    except Exception as e:
        print(f"❌ Model test error: {e}")
        return False

def test_fastapi_routes():
    """Test FastAPI app structure"""
    try:
        from app.main import app
        routes = [route.path for route in app.routes]
        expected = ["/send-otp", "/health", "/metrics", "/"]
        
        for route in expected:
            if route in routes:
                print(f"✅ Route exists: {route}")
            else:
                print(f"❌ Missing route: {route}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Route test error: {e}")
        return False

def main():
    print("=" * 60)
    print("OTP Social Gateway - Structure Validation")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Pydantic Models", test_pydantic_models),
        ("FastAPI Routes", test_fastapi_routes)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\nTesting: {name}")
        print("-" * 40)
        result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All validation tests passed!")
        print("\n📝 Next steps:")
        print("   1. Get Telegram Bot Token from @BotFather")
        print("   2. Create .env file with TELEGRAM_BOT_TOKEN")
        print("   3. Run: docker-compose up --build")
        print("   4. Test: curl http://localhost:55155/health")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
