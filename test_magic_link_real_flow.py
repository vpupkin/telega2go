#!/usr/bin/env python3
"""
🧪 Real Magic Link Flow Test (TDD)
==================================

This test creates a real Magic Link by going through the actual registration flow
and then tests the Magic Link verification.

Usage:
    python3 test_magic_link_real_flow.py
"""

import requests
import json
import time
import random
import string
from datetime import datetime

class RealMagicLinkFlowTester:
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

    def test_real_magic_link_flow(self):
        """Test the complete Magic Link flow with real registration"""
        self.log("🔍 Testing real Magic Link flow...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Real Magic Link Test {test_id}',
            'email': f'real_magic_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'real_magic_{test_id}'
        }
        
        try:
            # Step 1: Register user
            self.log("📝 Step 1: Registering user...")
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code != 200:
                self.log_error(f"Registration failed: {response.status_code}")
                self.log_error(f"Error: {response.text}")
                return False
            
            response_data = response.json()
            self.log_success("User registration successful")
            self.log(f"Response: {response_data}")
            
            # Step 2: Get the OTP from response
            otp = response_data.get('otp')
            if not otp:
                self.log_error("No OTP in registration response")
                return False
            
            self.log(f"Got OTP: {otp}")
            
            # Step 3: Verify OTP to complete registration and get Magic Link
            self.log("🔐 Step 3: Verifying OTP to get Magic Link...")
            verify_data = {
                'email': test_data['email'],
                'otp': otp
            }
            
            verify_response = requests.post(f"{self.backend_url}/api/verify-otp", json=verify_data, timeout=10)
            
            if verify_response.status_code != 200:
                self.log_error(f"OTP verification failed: {verify_response.status_code}")
                self.log_error(f"Error: {verify_response.text}")
                return False
            
            verify_result = verify_response.json()
            self.log_success("OTP verification successful")
            self.log(f"Verify result: {verify_result}")
            
            # Check if we got a Magic Link token
            magic_link = verify_result.get('magic_link')
            if not magic_link:
                self.log_error("No Magic Link in verification response")
                return False
            
            self.log(f"Got Magic Link: {magic_link[:50]}...")
            
            # Step 4: Test Magic Link verification
            self.log("🔗 Step 4: Testing Magic Link verification...")
            magic_verify_response = requests.post(f"{self.backend_url}/api/verify-magic-link", 
                                                params={"token": magic_link}, timeout=10)
            
            if magic_verify_response.status_code == 200:
                magic_result = magic_verify_response.json()
                self.log_success("✅ Magic Link verification successful!")
                self.log(f"Access token: {magic_result.get('access_token', 'None')[:20]}...")
                
                if 'user' in magic_result:
                    user = magic_result['user']
                    self.log_success(f"✅ User created: {user.get('name')}")
                    self.log_success(f"✅ User verified: {user.get('is_verified')}")
                    self.log_success(f"✅ Telegram chat ID: {user.get('telegram_chat_id')}")
                    return True
                else:
                    self.log_error("❌ No user data in Magic Link response")
                    return False
            else:
                self.log_error(f"❌ Magic Link verification failed: {magic_verify_response.status_code}")
                self.log_error(f"Error: {magic_verify_response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Real Magic Link flow test failed: {e}")
            return False

    def test_magic_link_with_chat_id_flow(self):
        """Test Magic Link flow with telegram chat ID"""
        self.log("🔍 Testing Magic Link flow with telegram chat ID...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Real Chat ID Magic Link Test {test_id}',
            'email': f'real_chatid_magic_{test_id}@example.com',
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
            
            # Step 2: Get the OTP from response
            otp = response_data.get('otp')
            if not otp:
                self.log_error("No OTP in registration response")
                return False
            
            # Step 3: Verify OTP to complete registration and get Magic Link
            self.log("🔐 Step 3: Verifying OTP to get Magic Link...")
            verify_data = {
                'email': test_data['email'],
                'otp': otp
            }
            
            verify_response = requests.post(f"{self.backend_url}/api/verify-otp", json=verify_data, timeout=10)
            
            if verify_response.status_code != 200:
                self.log_error(f"OTP verification failed: {verify_response.status_code}")
                return False
            
            verify_result = verify_response.json()
            self.log_success("OTP verification successful")
            
            # Check if we got a Magic Link token
            magic_link = verify_result.get('magic_link')
            if not magic_link:
                self.log_error("No Magic Link in verification response")
                return False
            
            # Step 4: Test Magic Link verification
            self.log("🔗 Step 4: Testing Magic Link verification...")
            magic_verify_response = requests.post(f"{self.backend_url}/api/verify-magic-link", 
                                                params={"token": magic_link}, timeout=10)
            
            if magic_verify_response.status_code == 200:
                magic_result = magic_verify_response.json()
                self.log_success("✅ Magic Link verification successful!")
                return True
            else:
                self.log_error(f"❌ Magic Link verification failed: {magic_verify_response.status_code}")
                self.log_error(f"Error: {magic_verify_response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Real Magic Link flow test failed: {e}")
            return False

    def run_real_magic_link_tests(self):
        """Run all real Magic Link flow tests"""
        self.log("🚀 Starting Real Magic Link Flow Tests (TDD)")
        self.log("=" * 60)
        
        tests = [
            ("Real Magic Link with Username", self.test_real_magic_link_flow),
            ("Real Magic Link with Chat ID", self.test_magic_link_with_chat_id_flow)
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
        self.log(f"📊 Real Magic Link Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_success("🎉 ALL REAL MAGIC LINK TESTS PASSED!")
            return True
        else:
            self.log_error(f"❌ {total - passed} real magic link tests failed!")
            return False

def main():
    """Main test execution function"""
    tester = RealMagicLinkFlowTester()
    
    try:
        success = tester.run_real_magic_link_tests()
        
        if success:
            tester.log_success("🎉 Real Magic Link flow test completed successfully!")
            exit(0)
        else:
            tester.log_error("❌ Real Magic Link flow test failed!")
            exit(1)
            
    except Exception as e:
        tester.log_error(f"Test execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
