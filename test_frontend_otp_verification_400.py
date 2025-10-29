#!/usr/bin/env python3
"""
🧪 Frontend OTP Verification 400 Error Test (TDD)
=================================================

This test reproduces the exact 400 Bad Request error from the frontend:
UserRegistration.jsx:112 POST http://localhost:5572/api/verify-otp 400 (Bad Request)

Usage:
    python3 test_frontend_otp_verification_400.py

TDD Approach:
1. RED: Reproduce the exact frontend error
2. GREEN: Fix the issue
3. REFACTOR: Improve while keeping tests green
"""

import requests
import json
import time
import random
import string
from datetime import datetime

class FrontendOTPVerification400Tester:
    def __init__(self):
        self.backend_url = "http://localhost:5572"
        self.frontend_url = "http://localhost:5573"
        
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

    def test_frontend_otp_verification_400_error(self):
        """Test the exact 400 error from frontend OTP verification"""
        self.log("🔍 Testing frontend OTP verification 400 error...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Frontend 400 Test {test_id}',
            'email': f'frontend_400_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'frontend_400_{test_id}'
        }
        
        try:
            # Step 1: Register user (simulate frontend registration)
            self.log("📝 Step 1: Registering user (frontend simulation)...")
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code != 200:
                self.log_error(f"Registration failed: {response.status_code} - {response.text}")
                return False
            
            response_data = response.json()
            self.log_success("User registration successful")
            self.log(f"Response: {response_data}")
            
            # Step 2: Try OTP verification with different scenarios
            self.log("🔐 Step 2: Testing OTP verification scenarios...")
            
            # Scenario 1: Try with empty OTP
            self.log("🧪 Scenario 1: Empty OTP")
            otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                'email': test_data['email'],
                'otp': ''
            }, timeout=10)
            
            self.log(f"Empty OTP response: {otp_response.status_code} - {otp_response.text}")
            
            # Scenario 2: Try with invalid OTP
            self.log("🧪 Scenario 2: Invalid OTP")
            otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                'email': test_data['email'],
                'otp': 'invalid'
            }, timeout=10)
            
            self.log(f"Invalid OTP response: {otp_response.status_code} - {otp_response.text}")
            
            # Scenario 3: Try with missing email
            self.log("🧪 Scenario 3: Missing email")
            otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                'otp': '123456'
            }, timeout=10)
            
            self.log(f"Missing email response: {otp_response.status_code} - {otp_response.text}")
            
            # Scenario 4: Try with wrong email
            self.log("🧪 Scenario 4: Wrong email")
            otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                'email': 'wrong@example.com',
                'otp': '123456'
            }, timeout=10)
            
            self.log(f"Wrong email response: {otp_response.status_code} - {otp_response.text}")
            
            # Scenario 5: Try with correct OTP (if available)
            if 'otp' in response_data:
                correct_otp = response_data['otp']
                self.log(f"🧪 Scenario 5: Correct OTP ({correct_otp})")
                otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                    'email': test_data['email'],
                    'otp': correct_otp
                }, timeout=10)
                
                self.log(f"Correct OTP response: {otp_response.status_code} - {otp_response.text}")
                
                if otp_response.status_code == 200:
                    self.log_success("✅ Correct OTP verification successful")
                    return True
                else:
                    self.log_error(f"❌ Correct OTP verification failed: {otp_response.text}")
                    return False
            else:
                self.log_warning("No OTP in registration response")
                return False
                
        except Exception as e:
            self.log_error(f"Frontend OTP verification test failed: {e}")
            return False

    def test_frontend_request_format(self):
        """Test the exact request format that frontend sends"""
        self.log("🔍 Testing frontend request format...")
        
        # Test the exact format that frontend sends
        test_data = {
            'name': 'Frontend Format Test',
            'email': 'frontend_format@example.com',
            'phone': '+1234567890',
            'telegram_username': 'frontend_format'
        }
        
        try:
            # Register user
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code == 200:
                response_data = response.json()
                self.log(f"Registration response: {response_data}")
                
                # Test OTP verification with exact frontend format
                otp_data = {
                    'email': test_data['email'],
                    'otp': '123456'  # Test OTP
                }
                
                self.log(f"Sending OTP verification with: {otp_data}")
                otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json=otp_data, timeout=10)
                
                self.log(f"OTP verification response: {otp_response.status_code}")
                self.log(f"OTP verification body: {otp_response.text}")
                
                if otp_response.status_code == 400:
                    self.log_error("❌ 400 Bad Request confirmed - this is the frontend error!")
                    return False
                else:
                    self.log_success("✅ No 400 error - issue may be resolved")
                    return True
            else:
                self.log_error(f"Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Frontend request format test failed: {e}")
            return False

    def test_backend_otp_verification_endpoint(self):
        """Test the backend OTP verification endpoint directly"""
        self.log("🔍 Testing backend OTP verification endpoint...")
        
        try:
            # Test with minimal data
            test_data = {
                'email': 'test@example.com',
                'otp': '123456'
            }
            
            response = requests.post(f"{self.backend_url}/api/verify-otp", json=test_data, timeout=10)
            
            self.log(f"Backend OTP verification response: {response.status_code}")
            self.log(f"Backend OTP verification body: {response.text}")
            
            if response.status_code == 400:
                self.log_error("❌ Backend returns 400 - this is the source of frontend error")
                return False
            else:
                self.log_success("✅ Backend OTP verification working")
                return True
                
        except Exception as e:
            self.log_error(f"Backend OTP verification test failed: {e}")
            return False

    def run_frontend_otp_400_tests(self):
        """Run all tests for frontend OTP verification 400 error"""
        self.log("🚀 Starting Frontend OTP Verification 400 Error Tests (TDD)")
        self.log("=" * 70)
        
        tests = [
            ("Frontend OTP Verification 400 Error", self.test_frontend_otp_verification_400_error),
            ("Frontend Request Format", self.test_frontend_request_format),
            ("Backend OTP Verification Endpoint", self.test_backend_otp_verification_endpoint)
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
        self.log("\n" + "=" * 70)
        self.log(f"📊 Frontend OTP 400 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_success("🎉 ALL FRONTEND OTP 400 TESTS PASSED!")
            return True
        else:
            self.log_error(f"❌ {total - passed} frontend OTP 400 tests failed!")
            return False

def main():
    """Main test execution function"""
    tester = FrontendOTPVerification400Tester()
    
    try:
        success = tester.run_frontend_otp_400_tests()
        
        if success:
            tester.log_success("🎉 Frontend OTP 400 test completed successfully!")
            exit(0)
        else:
            tester.log_error("❌ Frontend OTP 400 test failed!")
            exit(1)
            
    except Exception as e:
        tester.log_error(f"Test execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
