#!/usr/bin/env python3
"""
🧪 Magic Link Verification Test (TDD)
=====================================

This test verifies that Magic Link verification works correctly.
It tests the specific issue with telegram_chat_id being None.

Usage:
    python3 test_magic_link_verification.py
"""

import requests
import json
import time
import random
import string
import base64
import hmac
import hashlib
from datetime import datetime, timedelta, timezone

class MagicLinkVerificationTester:
    def __init__(self):
        self.backend_url = "http://localhost:5572"
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"ℹ️  [{timestamp}] {message}")
        
    def log_success(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"✅ [{timestamp}] {message}")
        
    def log_error(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"❌ [{timestamp}] {message}")
        
    def log_warning(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"⚠️  [{timestamp}] {message}")

    def create_magic_link_token(self, email, otp, expires_in_hours=1):
        """Create a magic link token for testing"""
        try:
            # Create token data
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
            token_data = {
                "email": email,
                "otp": otp,
                "expires_at": expires_at.timestamp()
            }
            
            # Encode token data
            token_json = json.dumps(token_data)
            token_b64 = base64.b64encode(token_json.encode()).decode()
            
            # Create signature (simplified for testing)
            signature = "test_signature"
            
            # Combine token and signature
            full_token = f"{token_b64}:{signature}"
            
            return full_token
            
        except Exception as e:
            self.log_error(f"Failed to create magic link token: {e}")
            return None

    def test_magic_link_verification_with_username(self):
        """Test Magic Link verification with telegram username (telegram_chat_id = None)"""
        self.log("🔍 Testing Magic Link verification with telegram username...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Magic Link Username Test {test_id}',
            'email': f'magic_username_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'magic_username_{test_id}'
        }
        
        try:
            # Step 1: Register user
            self.log("📝 Step 1: Registering user...")
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code != 200:
                self.log_error(f"Registration failed: {response.status_code}")
                return False
            
            response_data = response.json()
            self.log_success("User registration successful")
            
            # Step 2: Create magic link token
            self.log("🔗 Step 2: Creating magic link token...")
            otp = response_data.get('otp', '123456')
            magic_token = self.create_magic_link_token(test_data['email'], otp)
            
            if not magic_token:
                self.log_error("Failed to create magic link token")
                return False
            
            self.log(f"Magic token created: {magic_token[:50]}...")
            
            # Step 3: Test Magic Link verification
            self.log("🔐 Step 3: Testing Magic Link verification...")
            verify_response = requests.post(f"{self.backend_url}/api/verify-magic-link", 
                                          params={"token": magic_token}, timeout=10)
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                self.log_success("✅ Magic Link verification successful")
                self.log(f"Access token received: {verify_data.get('access_token', 'None')[:20]}...")
                
                if 'user' in verify_data:
                    user = verify_data['user']
                    self.log_success(f"✅ User created: {user.get('name')}")
                    self.log_success(f"✅ User verified: {user.get('is_verified')}")
                    return True
                else:
                    self.log_error("❌ No user data in response")
                    return False
            else:
                self.log_error(f"❌ Magic Link verification failed: {verify_response.status_code}")
                self.log_error(f"Error: {verify_response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Magic Link verification test failed: {e}")
            return False

    def test_magic_link_verification_with_chat_id(self):
        """Test Magic Link verification with telegram chat ID"""
        self.log("🔍 Testing Magic Link verification with telegram chat ID...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Magic Link Chat ID Test {test_id}',
            'email': f'magic_chatid_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_chat_id': f'{random.randint(100000000, 999999999)}'
        }
        
        try:
            # Step 1: Register user
            self.log("📝 Step 1: Registering user...")
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code != 200:
                self.log_error(f"Registration failed: {response.status_code}")
                return False
            
            response_data = response.json()
            self.log_success("User registration successful")
            
            # Step 2: Create magic link token
            self.log("🔗 Step 2: Creating magic link token...")
            otp = response_data.get('otp', '123456')
            magic_token = self.create_magic_link_token(test_data['email'], otp)
            
            if not magic_token:
                self.log_error("Failed to create magic link token")
                return False
            
            # Step 3: Test Magic Link verification
            self.log("🔐 Step 3: Testing Magic Link verification...")
            verify_response = requests.post(f"{self.backend_url}/api/verify-magic-link", 
                                          params={"token": magic_token}, timeout=10)
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                self.log_success("✅ Magic Link verification successful")
                return True
            else:
                self.log_error(f"❌ Magic Link verification failed: {verify_response.status_code}")
                self.log_error(f"Error: {verify_response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Magic Link verification test failed: {e}")
            return False

    def test_magic_link_with_invalid_token(self):
        """Test Magic Link verification with invalid token"""
        self.log("🔍 Testing Magic Link verification with invalid token...")
        
        try:
            # Test with invalid token
            invalid_token = "invalid_token_12345"
            verify_response = requests.post(f"{self.backend_url}/api/verify-magic-link", 
                                          params={"token": invalid_token}, timeout=10)
            
            if verify_response.status_code == 400:
                self.log_success("✅ Invalid token correctly rejected")
                return True
            else:
                self.log_error(f"❌ Invalid token not properly rejected: {verify_response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Invalid token test failed: {e}")
            return False

    def run_magic_link_tests(self):
        """Run all Magic Link verification tests"""
        self.log("🚀 Starting Magic Link Verification Tests (TDD)")
        self.log("=" * 60)
        
        tests = [
            ("Magic Link with Username", self.test_magic_link_verification_with_username),
            ("Magic Link with Chat ID", self.test_magic_link_verification_with_chat_id),
            ("Invalid Token Test", self.test_magic_link_with_invalid_token)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n🧪 Running: {test_name}")
            try:
                if test_func():
                    self.log_success(f"✅ {test_name} PASSED")
                    passed += 1
                else:
                    self.log_error(f"❌ {test_name} FAILED")
            except Exception as e:
                self.log_error(f"❌ {test_name} ERROR: {e}")
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log(f"📊 Magic Link Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_success("🎉 ALL MAGIC LINK TESTS PASSED!")
            return True
        else:
            self.log_error(f"❌ {total - passed} magic link tests failed!")
            return False

def main():
    """Main test execution function"""
    tester = MagicLinkVerificationTester()
    
    try:
        success = tester.run_magic_link_tests()
        
        if success:
            tester.log_success("🎉 Magic Link verification test completed successfully!")
            exit(0)
        else:
            tester.log_error("❌ Magic Link verification test failed!")
            exit(1)
            
    except Exception as e:
        tester.log_error(f"Test execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
