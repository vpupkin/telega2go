#!/usr/bin/env python3
"""
🧪 Frontend Complete Flow Test (TDD)
====================================

This test simulates the complete frontend flow:
1. User registration → gets real OTP
2. Frontend stores OTP → uses it for verification
3. OTP verification → should succeed

Usage:
    python3 test_frontend_complete_flow.py
"""

import requests
import json
import time
import random
import string
from datetime import datetime

class FrontendCompleteFlowTester:
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

    def test_complete_frontend_flow(self):
        """Test the complete frontend flow with real OTP"""
        self.log("🔍 Testing complete frontend flow...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Complete Flow Test {test_id}',
            'email': f'complete_flow_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'complete_flow_{test_id}'
        }
        
        try:
            # Step 1: User Registration (simulates frontend registration)
            self.log("📝 Step 1: User Registration")
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code != 200:
                self.log_error(f"Registration failed: {response.status_code} - {response.text}")
                return False
            
            response_data = response.json()
            self.log_success("User registration successful")
            
            # Extract OTP from response (simulates frontend behavior)
            real_otp = response_data.get('otp')
            if not real_otp:
                self.log_error("No OTP in registration response")
                return False
            
            self.log(f"📱 Real OTP received: {real_otp}")
            
            # Step 2: OTP Verification (simulates frontend using real OTP)
            self.log("🔐 Step 2: OTP Verification with real OTP")
            otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                'email': test_data['email'],
                'otp': real_otp  # Using the real OTP from registration
            }, timeout=10)
            
            if otp_response.status_code != 200:
                self.log_error(f"OTP verification failed: {otp_response.status_code} - {otp_response.text}")
                return False
            
            otp_data = otp_response.json()
            self.log_success("OTP verification successful")
            
            # Verify user account creation
            if 'user' in otp_data and 'access_token' in otp_data:
                user = otp_data['user']
                self.log_success(f"✅ User account created: {user['id']}")
                self.log_success(f"✅ User verified: {user['is_verified']}")
                self.log_success(f"✅ Access token received")
                return True
            else:
                self.log_error("User account creation incomplete")
                return False
                
        except Exception as e:
            self.log_error(f"Complete frontend flow test failed: {e}")
            return False

    def test_resend_otp_flow(self):
        """Test resend OTP flow with real OTP"""
        self.log("🔍 Testing resend OTP flow...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Resend Flow Test {test_id}',
            'email': f'resend_flow_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'resend_flow_{test_id}'
        }
        
        try:
            # Step 1: Register user
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code != 200:
                self.log_error(f"Registration failed: {response.status_code}")
                return False
            
            response_data = response.json()
            first_otp = response_data.get('otp')
            self.log(f"📱 First OTP: {first_otp}")
            
            # Step 2: Resend OTP
            self.log("📤 Step 2: Resending OTP")
            resend_response = requests.post(f"{self.backend_url}/api/resend-otp", json={
                'email': test_data['email']
            }, timeout=10)
            
            if resend_response.status_code != 200:
                self.log_error(f"Resend OTP failed: {resend_response.status_code}")
                return False
            
            resend_data = resend_response.json()
            second_otp = resend_data.get('otp')
            self.log(f"📱 Second OTP: {second_otp}")
            
            # Step 3: Verify with second OTP
            self.log("🔐 Step 3: Verifying with second OTP")
            otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                'email': test_data['email'],
                'otp': second_otp
            }, timeout=10)
            
            if otp_response.status_code == 200:
                self.log_success("✅ Resend OTP flow successful")
                return True
            else:
                self.log_error(f"❌ Resend OTP verification failed: {otp_response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Resend OTP flow test failed: {e}")
            return False

    def run_complete_flow_tests(self):
        """Run all complete flow tests"""
        self.log("🚀 Starting Frontend Complete Flow Tests (TDD)")
        self.log("=" * 60)
        
        tests = [
            ("Complete Frontend Flow", self.test_complete_frontend_flow),
            ("Resend OTP Flow", self.test_resend_otp_flow)
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
        self.log(f"📊 Complete Flow Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_success("🎉 ALL COMPLETE FLOW TESTS PASSED!")
            self.log_success("🚀 Frontend is working correctly with real OTPs!")
            return True
        else:
            self.log_error(f"❌ {total - passed} complete flow tests failed!")
            return False

def main():
    """Main test execution function"""
    tester = FrontendCompleteFlowTester()
    
    try:
        success = tester.run_complete_flow_tests()
        
        if success:
            tester.log_success("🎉 Frontend complete flow test completed successfully!")
            exit(0)
        else:
            tester.log_error("❌ Frontend complete flow test failed!")
            exit(1)
            
    except Exception as e:
        tester.log_error(f"Test execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
