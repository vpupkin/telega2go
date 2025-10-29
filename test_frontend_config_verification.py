#!/usr/bin/env python3
"""
Test Suite: Frontend Configuration Verification
Tests to ensure frontend uses correct backend URLs and ports after refactoring.
"""

import requests
import re
import subprocess
import sys
import os

class FrontendConfigTest:
    def __init__(self):
        self.frontend_url = "https://putana.date"
        self.backend_url = "https://putana.date:55552"
        self.old_port = "5572"
        self.new_port = "55552"
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Log test messages"""
        prefix = {
            "INFO": "ℹ️",
            "PASS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️"
        }.get(level, "ℹ️")
        print(f"{prefix} {message}")
        self.test_results.append({"level": level, "message": message})
    
    def test_frontend_build_has_no_old_ports(self):
        """Test 1: Verify frontend JavaScript bundle doesn't contain old port numbers"""
        self.log("=" * 60)
        self.log("TEST 1: Frontend Build Configuration Check")
        self.log("=" * 60)
        
        try:
            # Fetch the frontend HTML
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            
            # Extract JavaScript bundle URL from HTML
            js_url_match = re.search(r'src="(/static/js/[^"]+\.js)"', response.text)
            if not js_url_match:
                self.log("❌ Could not find JavaScript bundle URL in HTML", "FAIL")
                return False
            
            js_bundle_url = self.frontend_url + js_url_match.group(1)
            self.log(f"Found JavaScript bundle: {js_bundle_url}")
            
            # Fetch the JavaScript bundle
            js_response = requests.get(js_bundle_url, timeout=10)
            js_response.raise_for_status()
            js_content = js_response.text
            
            # Check for old port numbers
            old_port_patterns = [
                f"localhost:{self.old_port}",
                f":{self.old_port}",
                f"127.0.0.1:{self.old_port}",
                f"http://localhost:{self.old_port}",
                f"http://127.0.0.1:{self.old_port}"
            ]
            
            found_old_ports = []
            for pattern in old_port_patterns:
                if pattern in js_content:
                    matches = re.findall(re.escape(pattern), js_content)
                    found_old_ports.extend(matches)
            
            if found_old_ports:
                self.log(f"❌ Found old port {self.old_port} in JavaScript bundle!", "FAIL")
                self.log(f"Found patterns: {set(found_old_ports)}", "FAIL")
                return False
            
            # Check for correct new port (should be present)
            new_port_patterns = [
                f"putana.date:{self.new_port}",
                f":{self.new_port}",
                f"https://putana.date:{self.new_port}"
            ]
            
            found_new_ports = []
            for pattern in new_port_patterns:
                if pattern in js_content:
                    matches = re.findall(re.escape(pattern), js_content)
                    found_new_ports.extend(matches)
            
            if not found_new_ports:
                self.log(f"⚠️ Could not find new port {self.new_port} in bundle (may use relative URLs)", "WARN")
            else:
                self.log(f"✅ Found correct new port {self.new_port} configuration", "PASS")
            
            self.log("✅ JavaScript bundle does not contain old port numbers", "PASS")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch frontend: {e}", "FAIL")
            return False
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", "FAIL")
            return False
    
    def test_api_endpoints_use_correct_urls(self):
        """Test 2: Verify API endpoints use correct backend URLs"""
        self.log("=" * 60)
        self.log("TEST 2: API Endpoints Configuration Check")
        self.log("=" * 60)
        
        try:
            # Fetch frontend HTML
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            
            # Extract all JavaScript bundle URLs
            js_urls = re.findall(r'src="(/static/js/[^"]+\.js)"', response.text)
            if not js_urls:
                self.log("❌ Could not find JavaScript bundle URLs", "FAIL")
                return False
            
            all_correct = True
            
            for js_url in js_urls:
                full_url = self.frontend_url + js_url
                self.log(f"Checking bundle: {js_url}")
                
                try:
                    js_response = requests.get(full_url, timeout=10)
                    js_response.raise_for_status()
                    js_content = js_response.text
                    
                    # Check for API endpoint patterns
                    api_patterns = [
                        r'/api/(register|verify-otp|resend-otp|verify-magic-link)',
                        r'BACKEND_URL.*?=.*?["\']([^"\']+)["\']',
                        r'backend.*?["\']([^"\']+)["\']',
                        r'fetch\(["\']([^"\']*/api/[^"\']*)["\']'
                    ]
                    
                    found_incorrect = False
                    correct_urls_found = []
                    incorrect_urls_found = []
                    
                    for pattern in api_patterns:
                        matches = re.finditer(pattern, js_content, re.IGNORECASE)
                        for match in matches:
                            url = match.group(1) if len(match.groups()) > 0 else match.group(0)
                            
                            # Check if URL contains old port
                            if self.old_port in url:
                                incorrect_urls_found.append(url)
                                found_incorrect = True
                            elif self.new_port in url or 'putana.date/api' in url or '/api/' in url:
                                correct_urls_found.append(url)
                    
                    if found_incorrect:
                        self.log(f"❌ Found incorrect API URLs with old port:", "FAIL")
                        for url in incorrect_urls_found[:5]:  # Show first 5
                            self.log(f"   {url}", "FAIL")
                        all_correct = False
                    elif correct_urls_found:
                        self.log(f"✅ Found correct API URL patterns", "PASS")
                        # Show a sample
                        if correct_urls_found:
                            self.log(f"   Example: {correct_urls_found[0][:80]}...", "INFO")
                    
                except Exception as e:
                    self.log(f"⚠️ Could not check bundle {js_url}: {e}", "WARN")
                    continue
            
            if all_correct:
                self.log("✅ All API endpoints use correct backend URLs", "PASS")
            else:
                self.log("❌ Some API endpoints use incorrect URLs", "FAIL")
            
            return all_correct
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch frontend: {e}", "FAIL")
            return False
        except Exception as e:
            self.log(f"❌ Unexpected error: {e}", "FAIL")
            return False
    
    def test_backend_actual_connectivity(self):
        """Test 3: Verify backend is actually accessible on new port"""
        self.log("=" * 60)
        self.log("TEST 3: Backend Connectivity Check")
        self.log("=" * 60)
        
        try:
            # Test direct backend access
            backend_response = requests.get(f"{self.backend_url}/api/", timeout=10)
            backend_response.raise_for_status()
            self.log(f"✅ Backend accessible on port {self.new_port}", "PASS")
            
            # Test via Apache2 proxy
            proxy_response = requests.get(f"{self.frontend_url}/api/", timeout=10)
            proxy_response.raise_for_status()
            self.log(f"✅ Backend accessible via Apache2 proxy at /api/", "PASS")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Backend connectivity test failed: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🚀 FRONTEND CONFIGURATION VERIFICATION TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # Test 1: Frontend build configuration
        results.append(("Frontend Build Check", self.test_frontend_build_has_no_old_ports()))
        
        # Test 2: API endpoints configuration
        results.append(("API Endpoints Check", self.test_api_endpoints_use_correct_urls()))
        
        # Test 3: Backend connectivity
        results.append(("Backend Connectivity", self.test_backend_actual_connectivity()))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print("\n" + "=" * 60)
        print(f"Results: {passed}/{total} tests passed")
        print("=" * 60 + "\n")
        
        return passed == total

if __name__ == "__main__":
    tester = FrontendConfigTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

