#!/usr/bin/env python3
"""
🚀 Telega2Go Complete Automation Test Suite
===========================================

This is the ULTIMATE automated testing solution that eliminates ALL manual testing.
It provides comprehensive testing of the entire system using multiple approaches.

Usage:
    python3 test_complete_automation.py

Features:
- Complete API flow testing
- Frontend functionality testing
- Error handling testing
- Performance testing
- Integration testing
- No manual intervention required
- Comprehensive reporting
- Automatic test data generation
"""

import requests
import json
import time
import random
import string
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class CompleteAutomationTester:
    def __init__(self):
        self.base_url = "http://localhost:5573"
        self.backend_url = "http://localhost:5572"
        self.otp_gateway_url = "http://localhost:5571"
        self.test_results = []
        self.start_time = datetime.now()
        
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

    def run_command(self, command, description=""):
        """Run a shell command and return the result"""
        try:
            self.log(f"🔧 Running: {description or command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.log_success(f"Command successful: {description or command}")
                return True, result.stdout
            else:
                self.log_error(f"Command failed: {description or command}")
                self.log_error(f"Error: {result.stderr}")
                return False, result.stderr
        except subprocess.TimeoutExpired:
            self.log_error(f"Command timeout: {description or command}")
            return False, "Timeout"
        except Exception as e:
            self.log_error(f"Command exception: {e}")
            return False, str(e)

    def test_system_health(self):
        """Test complete system health"""
        self.log("🔍 Testing complete system health...")
        
        health_checks = [
            ("Backend API", f"{self.backend_url}/api/"),
            ("Frontend", self.base_url),
            ("OTP Gateway", f"{self.otp_gateway_url}/health"),
            ("MongoDB", f"{self.backend_url}/api/")  # Backend depends on MongoDB
        ]
        
        all_healthy = True
        for service_name, url in health_checks:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    self.log_success(f"{service_name} is healthy")
                else:
                    self.log_error(f"{service_name} returned {response.status_code}")
                    all_healthy = False
            except Exception as e:
                self.log_error(f"{service_name} is not responding: {e}")
                all_healthy = False
        
        return all_healthy

    def test_complete_user_journey(self):
        """Test the complete user journey from registration to verification"""
        self.log("🔍 Testing complete user journey...")
        
        # Generate unique test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Complete Test User {test_id}',
            'email': f'complete_test_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'complete_test_{test_id}'
        }
        
        try:
            # Step 1: User Registration
            self.log("📝 Step 1: User Registration")
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code != 200:
                self.log_error(f"Registration failed: {response.status_code} - {response.text}")
                return False
            
            self.log_success("User registration successful")
            response_data = response.json()
            
            # Step 2: Get OTP for verification
            otp_code = None
            if 'otp' in response_data:
                otp_code = response_data['otp']
                self.log(f"📱 OTP received: {otp_code}")
            else:
                self.log_warning("No OTP in response, using test OTP")
                otp_code = "123456"
            
            # Step 3: OTP Verification
            self.log("🔐 Step 3: OTP Verification")
            otp_response = requests.post(f"{self.backend_url}/api/verify-otp", json={
                'email': test_data['email'],
                'otp': otp_code
            }, timeout=10)
            
            if otp_response.status_code != 200:
                self.log_error(f"OTP verification failed: {otp_response.status_code} - {otp_response.text}")
                return False
            
            self.log_success("OTP verification successful")
            otp_data = otp_response.json()
            
            # Step 4: Verify user account creation
            if 'user' in otp_data and 'access_token' in otp_data:
                user = otp_data['user']
                self.log_success(f"User account created: {user['id']}")
                self.log_success(f"User verified: {user['is_verified']}")
                self.log_success(f"User name: {user['name']}")
                self.log_success(f"User email: {user['email']}")
                return True
            else:
                self.log_error("User account creation incomplete")
                return False
                
        except Exception as e:
            self.log_error(f"Complete user journey test failed: {e}")
            return False

    def test_resend_otp_functionality(self):
        """Test resend OTP functionality"""
        self.log("🔍 Testing resend OTP functionality...")
        
        # Generate test data
        test_id = ''.join(random.choices(string.digits, k=8))
        test_data = {
            'name': f'Resend Test User {test_id}',
            'email': f'resend_test_{test_id}@example.com',
            'phone': f'+1{random.randint(1000000000, 9999999999)}',
            'telegram_username': f'resend_test_{test_id}'
        }
        
        try:
            # Register user
            response = requests.post(f"{self.backend_url}/api/register", json=test_data, timeout=10)
            
            if response.status_code != 200:
                self.log_error(f"Registration failed for resend test: {response.status_code}")
                return False
            
            # Resend OTP
            resend_response = requests.post(f"{self.backend_url}/api/resend-otp", json={
                'email': test_data['email']
            }, timeout=10)
            
            if resend_response.status_code == 200:
                self.log_success("OTP resend successful")
                return True
            else:
                self.log_error(f"OTP resend failed: {resend_response.status_code} - {resend_response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Resend OTP test failed: {e}")
            return False

    def test_error_handling(self):
        """Test comprehensive error handling"""
        self.log("🔍 Testing comprehensive error handling...")
        
        error_tests = [
            {
                'name': 'Invalid email format',
                'data': {'name': 'Test', 'email': 'invalid-email', 'phone': '+1234567890', 'telegram_username': 'test'},
                'expected_status': 422
            },
            {
                'name': 'Missing required fields',
                'data': {'name': 'Test'},
                'expected_status': 422
            },
            {
                'name': 'Invalid OTP',
                'data': {'email': 'nonexistent@example.com', 'otp': 'invalid'},
                'expected_status': 400,
                'endpoint': '/api/verify-otp'
            },
            {
                'name': 'Invalid Magic Link token',
                'data': {},
                'expected_status': 400,
                'endpoint': '/api/verify-magic-link?token=invalid',
                'method': 'POST'
            }
        ]
        
        passed = 0
        for test in error_tests:
            try:
                endpoint = test.get('endpoint', '/api/register')
                method = test.get('method', 'POST')
                url = f"{self.backend_url}{endpoint}"
                
                if method == 'POST':
                    response = requests.post(url, json=test['data'], timeout=5)
                else:
                    response = requests.get(url, timeout=5)
                
                if response.status_code == test['expected_status']:
                    self.log_success(f"✅ {test['name']} - Correctly rejected")
                    passed += 1
                else:
                    self.log_error(f"❌ {test['name']} - Expected {test['expected_status']}, got {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"❌ {test['name']} - Exception: {e}")
        
        self.log(f"Error handling: {passed}/{len(error_tests)} tests passed")
        return passed == len(error_tests)

    def test_performance(self):
        """Test system performance"""
        self.log("🔍 Testing system performance...")
        
        try:
            # Test response times
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/api/", timeout=5)
            backend_time = time.time() - start_time
            
            start_time = time.time()
            response = requests.get(self.base_url, timeout=5)
            frontend_time = time.time() - start_time
            
            start_time = time.time()
            response = requests.get(f"{self.otp_gateway_url}/health", timeout=5)
            otp_time = time.time() - start_time
            
            self.log(f"Backend response time: {backend_time:.2f}s")
            self.log(f"Frontend response time: {frontend_time:.2f}s")
            self.log(f"OTP Gateway response time: {otp_time:.2f}s")
            
            # Check if response times are acceptable (under 2 seconds)
            if backend_time < 2 and frontend_time < 2 and otp_time < 2:
                self.log_success("Performance test passed")
                return True
            else:
                self.log_warning("Performance test warning - slow response times")
                return False
                
        except Exception as e:
            self.log_error(f"Performance test failed: {e}")
            return False

    def test_docker_services(self):
        """Test Docker services status"""
        self.log("🔍 Testing Docker services...")
        
        # Check if all required containers are running
        success, output = self.run_command("docker compose ps --format json", "Check container status")
        
        if not success:
            self.log_error("Failed to check Docker services")
            return False
        
        try:
            # Parse JSON output line by line (docker compose ps --format json outputs one JSON per line)
            containers = []
            for line in output.strip().split('\n'):
                if line.strip():
                    try:
                        containers.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            required_services = ['backend', 'frontend', 'otp-gateway', 'mongodb']
            
            running_services = []
            for container in containers:
                if container.get('State') == 'running':
                    service_name = container.get('Name', '').replace('telega2go-', '')
                    running_services.append(service_name)
            
            missing_services = set(required_services) - set(running_services)
            
            if not missing_services:
                self.log_success("All required Docker services are running")
                return True
            else:
                self.log_error(f"Missing services: {missing_services}")
                return False
                
        except Exception as e:
            self.log_error(f"Docker services check failed: {e}")
            return False

    def run_comprehensive_test_suite(self):
        """Run the complete automated test suite"""
        self.log("🚀 Starting Complete Automation Test Suite")
        self.log("=" * 60)
        
        tests = [
            ("System Health", self.test_system_health),
            ("Docker Services", self.test_docker_services),
            ("Complete User Journey", self.test_complete_user_journey),
            ("Resend OTP Functionality", self.test_resend_otp_functionality),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance)
        ]
        
        passed = 0
        total = len(tests)
        results = []
        
        for test_name, test_func in tests:
            self.log(f"\n🧪 Running: {test_name}")
            try:
                start_time = time.time()
                success = test_func()
                duration = time.time() - start_time
                
                results.append({
                    'name': test_name,
                    'passed': success,
                    'duration': duration
                })
                
                if success:
                    self.log_success(f"✅ {test_name} PASSED ({duration:.2f}s)")
                    passed += 1
                else:
                    self.log_error(f"❌ {test_name} FAILED ({duration:.2f}s)")
                    
            except Exception as e:
                self.log_error(f"❌ {test_name} ERROR: {e}")
                results.append({
                    'name': test_name,
                    'passed': False,
                    'duration': 0,
                    'error': str(e)
                })
        
        # Generate comprehensive report
        self.generate_report(results, passed, total)
        
        # Summary
        self.log("\n" + "=" * 60)
        self.log(f"📊 Final Results: {passed}/{total} tests passed")
        
        if passed == total:
            self.log_success("🎉 ALL TESTS PASSED! System is fully functional!")
            return True
        else:
            self.log_error(f"❌ {total - passed} tests failed!")
            return False

    def generate_report(self, results, passed, total):
        """Generate a comprehensive test report"""
        self.log("📊 Generating comprehensive test report...")
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        report = {
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'summary': {
                'total_tests': total,
                'passed': passed,
                'failed': total - passed,
                'success_rate': f"{(passed/total)*100:.1f}%"
            },
            'results': results,
            'system_info': {
                'backend_url': self.backend_url,
                'frontend_url': self.base_url,
                'otp_gateway_url': self.otp_gateway_url
            }
        }
        
        # Save report
        with open('complete_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save summary
        with open('test_summary.txt', 'w') as f:
            f.write(f"Telega2Go Complete Automation Test Report\n")
            f.write(f"==========================================\n\n")
            f.write(f"Timestamp: {end_time.isoformat()}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)\n\n")
            f.write(f"Test Results:\n")
            for result in results:
                status = "PASS" if result['passed'] else "FAIL"
                f.write(f"  {status}: {result['name']} ({result['duration']:.2f}s)\n")
                if 'error' in result:
                    f.write(f"    Error: {result['error']}\n")
        
        self.log(f"📄 Test report saved: complete_test_report.json")
        self.log(f"📄 Test summary saved: test_summary.txt")

def main():
    """Main test execution function"""
    tester = CompleteAutomationTester()
    
    try:
        success = tester.run_comprehensive_test_suite()
        
        if success:
            tester.log_success("🎉 Complete automation test completed successfully!")
            exit(0)
        else:
            tester.log_error("❌ Complete automation test failed!")
            exit(1)
            
    except Exception as e:
        tester.log_error(f"Test suite execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
