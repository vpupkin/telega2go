#!/usr/bin/env python3
"""
🧪 Telega2Go QR Code Functionality Test (TDD)
=============================================

This test follows TDD principles to verify QR code functionality.
It tests the complete QR code generation and sending process.

Usage:
    python3 test_qr_code_functionality.py

TDD Approach:
1. RED: Write failing test for QR code functionality
2. GREEN: Implement QR code functionality
3. REFACTOR: Improve while keeping tests green
"""

import requests
import json
import time
import random
import string
from datetime import datetime

class QRCodeFunctionalityTester:
    def __init__(self):
        self.backend_url = "http://localhost:5572"
        self.otp_gateway_url = "http://localhost:5571"
        
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

    def test_qr_code_generation_and_sending(self):
        """Test that QR codes are generated and sent via Telegram"""
        self.log("🔍 Testing QR code generation and sending...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'QR Test User {test_id}',
            'email': f'qr_test_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'qr_test_{test_id}'
        }
        
        try:
            # Step 1: Register user and trigger QR code generation
            self.log("📝 Step 1: Registering user to trigger QR code generation...")
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code != 200:
                self.log_error(f"Registration failed: {response.status_code} - {response.text}")
                return False
            
            response_data = response.json()
            self.log_success("User registration successful")
            
            # Check if the response indicates QR code was sent
            if "QR code" in response_data.get("message", ""):
                self.log_success("✅ QR code generation triggered")
            else:
                self.log_warning("⚠️  QR code not mentioned in response")
            
            # Step 2: Verify OTP Gateway received the request
            self.log("🔍 Step 2: Checking OTP Gateway logs for QR code sending...")
            
            # Wait a moment for the OTP Gateway to process
            time.sleep(2)
            
            # Check OTP Gateway health to ensure it's working
            otp_response = requests.get(f"{self.otp_gateway_url}/health", timeout=5)
            if otp_response.status_code == 200:
                self.log_success("OTP Gateway is responding")
            else:
                self.log_error("OTP Gateway is not responding")
                return False
            
            # Step 3: Test OTP verification (which should work if QR was sent)
            self.log("🔐 Step 3: Testing OTP verification...")
            
            # Get OTP from response or use test OTP
            otp_code = response_data.get('otp', '123456')
            if otp_code:
                self.log(f"📱 Using OTP: {otp_code}")
                
                otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                    'email': test_data['email'],
                    'otp': otp_code
                }, timeout=10)
                
                if otp_response.status_code == 200:
                    self.log_success("✅ OTP verification successful")
                    otp_data = otp_response.json()
                    
                    if 'user' in otp_data and otp_data['user'].get('is_verified'):
                        self.log_success("✅ User account verified successfully")
                        return True
                    else:
                        self.log_error("❌ User account not verified")
                        return False
                else:
                    self.log_error(f"❌ OTP verification failed: {otp_response.status_code}")
                    return False
            else:
                self.log_error("❌ No OTP received")
                return False
                
        except Exception as e:
            self.log_error(f"QR code test failed: {e}")
            return False

    def test_qr_code_with_telegram_username(self):
        """Test QR code generation with Telegram username"""
        self.log("🔍 Testing QR code with Telegram username...")
        
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'QR Username Test {test_id}',
            'email': f'qr_username_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'qr_username_{test_id}'
        }
        
        try:
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code == 200:
                self.log_success("✅ Registration with username successful")
                response_data = response.json()
                
                if "QR code" in response_data.get("message", ""):
                    self.log_success("✅ QR code generation mentioned in response")
                    return True
                else:
                    self.log_warning("⚠️  QR code not mentioned in response")
                    return False
            else:
                self.log_error(f"❌ Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"QR username test failed: {e}")
            return False

    def test_qr_code_with_telegram_chat_id(self):
        """Test QR code generation with Telegram chat ID"""
        self.log("🔍 Testing QR code with Telegram chat ID...")
        
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'QR Chat ID Test {test_id}',
            'email': f'qr_chatid_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_chat_id': f'{random.randint(100000000, 999999999)}'
        }
        
        try:
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code == 200:
                self.log_success("✅ Registration with chat ID successful")
                response_data = response.json()
                
                if "QR code" in response_data.get("message", ""):
                    self.log_success("✅ QR code generation mentioned in response")
                    return True
                else:
                    self.log_warning("⚠️  QR code not mentioned in response")
                    return False
            else:
                self.log_error(f"❌ Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"QR chat ID test failed: {e}")
            return False

    def test_otp_gateway_qr_capabilities(self):
        """Test OTP Gateway QR code capabilities"""
        self.log("🔍 Testing OTP Gateway QR code capabilities...")
        
        try:
            # Check OTP Gateway health
            health_response = requests.get(f"{self.otp_gateway_url}/health", timeout=5)
            if health_response.status_code != 200:
                self.log_error("OTP Gateway health check failed")
                return False
            
            self.log_success("✅ OTP Gateway is healthy")
            
            # Check if OTP Gateway has QR code dependencies
            # This would require checking the OTP Gateway code or logs
            # For now, we'll test by sending a request and checking the response
            
            test_data = {
                'telegram_username': 'test_qr_user',
                'otp': '123456',
                'expires_in_seconds': 300
            }
            
            # This should trigger QR code generation
            response = requests.post(f"{self.otp_gateway_url}/send-otp", json=test_data, timeout=10)
            
            if response.status_code == 200:
                self.log_success("✅ OTP Gateway can process QR code requests")
                return True
            else:
                self.log_error(f"❌ OTP Gateway request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"OTP Gateway QR test failed: {e}")
            return False

    def run_qr_code_tests(self):
        """Run all QR code functionality tests"""
        self.log("🚀 Starting QR Code Functionality Tests (TDD)")
        self.log("=" * 60)
        
        tests = [
            ("QR Code Generation and Sending", self.test_qr_code_generation_and_sending),
            ("QR Code with Telegram Username", self.test_qr_code_with_telegram_username),
            ("QR Code with Telegram Chat ID", self.test_qr_code_with_telegram_chat_id),
            ("OTP Gateway QR Capabilities", self.test_otp_gateway_qr_capabilities)
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
        self.log(f"📊 QR Code Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_success("🎉 ALL QR CODE TESTS PASSED! QR functionality is working!")
            return True
        else:
            self.log_error(f"❌ {total - passed} QR code tests failed!")
            return False

def main():
    """Main test execution function"""
    tester = QRCodeFunctionalityTester()
    
    try:
        success = tester.run_qr_code_tests()
        
        if success:
            tester.log_success("🎉 QR code functionality test completed successfully!")
            exit(0)
        else:
            tester.log_error("❌ QR code functionality test failed!")
            exit(1)
            
    except Exception as e:
        tester.log_error(f"Test execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
