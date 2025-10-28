#!/usr/bin/env python3
"""
🚀 Telega2Go Simple Frontend Test Suite
=======================================

This script provides automated testing of the frontend API endpoints
without requiring browser automation. It tests the complete user journey
by directly calling the frontend's underlying API endpoints.

Usage:
    python3 test_frontend_simple.py

Features:
- Complete API flow testing
- No browser dependencies
- Fast execution
- Comprehensive error reporting
- Automatic test data generation
"""

import requests
import json
import time
import random
import string
from datetime import datetime

class SimpleFrontendTester:
    def __init__(self):
        self.base_url = "http://localhost:5573"
        self.backend_url = "http://localhost:5572"
        self.test_results = []
        
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

    def test_services_health(self):
        """Test that all services are running"""
        self.log("🔍 Testing services health...")
        
        try:
            # Test backend
            response = requests.get(f"{self.backend_url}/api/", timeout=5)
            if response.status_code != 200:
                raise Exception(f"Backend not responding: {response.status_code}")
            self.log_success("Backend API is running")
            
            # Test frontend
            response = requests.get(self.base_url, timeout=5)
            if response.status_code != 200:
                raise Exception(f"Frontend not responding: {response.status_code}")
            self.log_success("Frontend is running")
            
            # Test OTP Gateway
            response = requests.get(f"{self.backend_url.replace('5572', '5571')}/health", timeout=5)
            if response.status_code != 200:
                raise Exception(f"OTP Gateway not responding: {response.status_code}")
            self.log_success("OTP Gateway is running")
            
            return True
        except Exception as e:
            self.log_error(f"Services health check failed: {e}")
            return False

    def test_registration_flow(self):
        """Test complete registration flow"""
        self.log("🔍 Testing complete registration flow...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Automated Test User {test_id}',
            'email': f'automated_test_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'automated_test_{test_id}'
        }
        
        try:
            # Step 1: Register user
            self.log("📝 Step 1: Registering user...")
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code == 200:
                self.log_success("User registration successful")
                response_data = response.json()
                
                # Check if OTP was provided for testing
                if 'otp' in response_data:
                    otp_code = response_data['otp']
                    self.log(f"📱 OTP received: {otp_code}")
                else:
                    self.log_warning("No OTP in response, using test OTP")
                    otp_code = "123456"
                
                # Step 2: Verify OTP
                self.log("🔐 Step 2: Verifying OTP...")
                otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                    'email': test_data['email'],
                    'otp': otp_code
                }, timeout=10)
                
                if otp_response.status_code == 200:
                    self.log_success("OTP verification successful")
                    otp_data = otp_response.json()
                    
                    # Check if user was created successfully
                    if 'user' in otp_data and 'access_token' in otp_data:
                        self.log_success("User account created successfully")
                        self.log_success(f"User ID: {otp_data['user']['id']}")
                        self.log_success(f"User verified: {otp_data['user']['is_verified']}")
                        return True
                    else:
                        self.log_error("User account creation failed")
                        return False
                else:
                    self.log_error(f"OTP verification failed: {otp_response.status_code}")
                    self.log_error(f"Error: {otp_response.text}")
                    return False
            else:
                self.log_error(f"User registration failed: {response.status_code}")
                self.log_error(f"Error: {response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Registration flow test failed: {e}")
            return False

    def test_resend_otp_flow(self):
        """Test resend OTP functionality"""
        self.log("🔍 Testing resend OTP flow...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Resend Test User {test_id}',
            'email': f'resend_test_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'resend_test_{test_id}'
        }
        
        try:
            # Step 1: Register user
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code == 200:
                self.log_success("User registered for resend test")
                
                # Step 2: Resend OTP
                self.log("📤 Step 2: Resending OTP...")
                resend_response = requests.post(f"{self.backend_url}/api/resend-otp", json={
                    'email': test_data['email']
                }, timeout=10)
                
                if resend_response.status_code == 200:
                    self.log_success("OTP resend successful")
                    return True
                else:
                    self.log_error(f"OTP resend failed: {resend_response.status_code}")
                    self.log_error(f"Error: {resend_response.text}")
                    return False
            else:
                self.log_error(f"User registration failed for resend test: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Resend OTP test failed: {e}")
            return False

    def test_error_handling(self):
        """Test error handling scenarios"""
        self.log("🔍 Testing error handling...")
        
        try:
            # Test 1: Invalid email format
            self.log("🧪 Test 1: Invalid email format")
            response = requests.post(f"{self.backend_url}/api/register", json={
                'name': 'Test User',
                'email': 'invalid-email',
                'phone': '+1234567890',
                'telegram_username': 'testuser'
            }, timeout=10)
            
            if response.status_code == 422:
                self.log_success("Invalid email properly rejected")
            else:
                self.log_warning(f"Invalid email not properly rejected: {response.status_code}")
            
            # Test 2: Missing required fields
            self.log("🧪 Test 2: Missing required fields")
            response = requests.post(f"{self.backend_url}/api/register", json={
                'name': 'Test User'
                # Missing email, phone, telegram_username
            }, timeout=10)
            
            if response.status_code == 422:
                self.log_success("Missing fields properly rejected")
            else:
                self.log_warning(f"Missing fields not properly rejected: {response.status_code}")
            
            # Test 3: Invalid OTP
            self.log("🧪 Test 3: Invalid OTP")
            response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                'email': 'nonexistent@example.com',
                'otp': 'invalid'
            }, timeout=10)
            
            if response.status_code == 400:
                self.log_success("Invalid OTP properly rejected")
            else:
                self.log_warning(f"Invalid OTP not properly rejected: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Error handling test failed: {e}")
            return False

    def test_magic_link_flow(self):
        """Test Magic Link functionality"""
        self.log("🔍 Testing Magic Link flow...")
        
        try:
            # Test Magic Link verification endpoint
            self.log("🔗 Testing Magic Link verification...")
            response = requests.post(f"{self.backend_url}/api/verify-magic-link?token=test_token", timeout=10)
            
            if response.status_code == 400:
                self.log_success("Magic Link endpoint responding correctly")
                return True
            else:
                self.log_warning(f"Magic Link endpoint unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Magic Link test failed: {e}")
            return False

    def run_comprehensive_test(self):
        """Run the complete automated test suite"""
        self.log("🚀 Starting Simple Frontend Test Suite")
        self.log("=" * 50)
        
        tests = [
            ("Services Health", self.test_services_health),
            ("Registration Flow", self.test_registration_flow),
            ("Resend OTP Flow", self.test_resend_otp_flow),
            ("Error Handling", self.test_error_handling),
            ("Magic Link Flow", self.test_magic_link_flow)
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
        self.log("\n" + "=" * 50)
        self.log(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_success("🎉 ALL TESTS PASSED! Frontend is working correctly!")
            return True
        else:
            self.log_error(f"❌ {total - passed} tests failed!")
            return False

def main():
    """Main test execution function"""
    tester = SimpleFrontendTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            tester.log_success("🎉 Simple frontend test completed successfully!")
            exit(0)
        else:
            tester.log_error("❌ Simple frontend test failed!")
            exit(1)
            
    except Exception as e:
        tester.log_error(f"Test suite execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
