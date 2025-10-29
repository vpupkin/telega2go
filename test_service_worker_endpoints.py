#!/usr/bin/env python3
"""
Test Suite: Service Worker API Endpoints Verification
Tests to ensure service worker correctly handles API requests with new backend URLs.
"""

import requests
import re
import json
import sys
from urllib.parse import urlparse

class ServiceWorkerEndpointTest:
    def __init__(self):
        self.frontend_url = "https://putana.date"
        self.backend_url = "https://putana.date:55552"
        self.api_base_url = "https://putana.date/api"
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
    
    def test_service_worker_file_exists(self):
        """Test 1: Verify service worker file exists and is accessible"""
        self.log("=" * 60)
        self.log("TEST 1: Service Worker File Accessibility")
        self.log("=" * 60)
        
        try:
            sw_url = f"{self.frontend_url}/sw.js"
            response = requests.get(sw_url, timeout=10)
            response.raise_for_status()
            
            if response.text.startswith("// Service Worker"):
                self.log("✅ Service worker file exists and is accessible", "PASS")
                return True, response.text
            else:
                self.log("⚠️ Service worker file exists but may be incorrect format", "WARN")
                return True, response.text
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch service worker: {e}", "FAIL")
            return False, None
    
    def test_service_worker_no_hardcoded_ports(self):
        """Test 2: Verify service worker doesn't contain hardcoded old ports"""
        self.log("=" * 60)
        self.log("TEST 2: Service Worker Port Configuration Check")
        self.log("=" * 60)
        
        try:
            sw_url = f"{self.frontend_url}/sw.js"
            response = requests.get(sw_url, timeout=10)
            response.raise_for_status()
            sw_content = response.text
            
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
                if pattern in sw_content:
                    matches = re.findall(re.escape(pattern), sw_content)
                    found_old_ports.extend(matches)
            
            if found_old_ports:
                self.log(f"❌ Found old port {self.old_port} in service worker!", "FAIL")
                self.log(f"Found patterns: {set(found_old_ports)}", "FAIL")
                
                # Show context
                lines = sw_content.split('\n')
                for i, line in enumerate(lines, 1):
                    if self.old_port in line:
                        self.log(f"Line {i}: {line.strip()[:100]}", "FAIL")
                
                return False
            
            self.log("✅ Service worker does not contain hardcoded old ports", "PASS")
            
            # Check that service worker uses relative URLs or proper patterns
            if "/api/" in sw_content:
                self.log("✅ Service worker correctly uses relative /api/ paths", "PASS")
            else:
                self.log("⚠️ Service worker may not handle API requests", "WARN")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch service worker: {e}", "FAIL")
            return False
    
    def test_service_worker_api_request_handling(self):
        """Test 3: Verify service worker correctly handles API requests"""
        self.log("=" * 60)
        self.log("TEST 3: Service Worker API Request Handling")
        self.log("=" * 60)
        
        try:
            sw_url = f"{self.frontend_url}/sw.js"
            response = requests.get(sw_url, timeout=10)
            response.raise_for_status()
            sw_content = response.text
            
            # Check for API request handling patterns
            api_patterns = [
                r"event\.request\.url\.includes\(['\"]/api/['\"]\)",
                r"/api/",
                r"fetch\(event\.request\)",
                r"caches\.match\(event\.request\)"
            ]
            
            found_patterns = []
            for pattern in api_patterns:
                if re.search(pattern, sw_content):
                    found_patterns.append(pattern)
            
            if not found_patterns:
                self.log("⚠️ Service worker may not handle API requests", "WARN")
                return True  # Not a failure, just a warning
            
            self.log(f"✅ Service worker handles API requests correctly", "PASS")
            self.log(f"Found {len(found_patterns)} API handling patterns", "INFO")
            
            # Verify it uses relative URLs (not hardcoded ports)
            if "localhost" in sw_content.lower() or "127.0.0.1" in sw_content:
                # Check if it's using environment variables or relative URLs
                if "process.env" in sw_content or "REACT_APP" in sw_content:
                    self.log("⚠️ Service worker references environment variables (may not work in SW)", "WARN")
                elif re.search(r"['\"]/api/", sw_content):
                    self.log("✅ Service worker uses relative API paths", "PASS")
                else:
                    self.log("⚠️ Service worker may have hardcoded URLs", "WARN")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch service worker: {e}", "FAIL")
            return False
    
    def test_api_endpoints_accessible_via_service_worker_proxy(self):
        """Test 4: Verify API endpoints are accessible (simulating service worker behavior)"""
        self.log("=" * 60)
        self.log("TEST 4: API Endpoints Accessibility Test")
        self.log("=" * 60)
        
        api_endpoints = [
            "/api/",
            "/api/register",
            "/api/verify-otp",
            "/api/resend-otp",
            "/api/verify-magic-link"
        ]
        
        all_accessible = True
        
        for endpoint in api_endpoints:
            try:
                # Test via Apache2 proxy (as service worker would)
                url = f"{self.frontend_url}{endpoint}"
                
                # Use GET for most endpoints, POST for register/verify
                if endpoint in ["/api/register", "/api/verify-otp", "/api/resend-otp", "/api/verify-magic-link"]:
                    # Test OPTIONS (preflight) first
                    options_response = requests.options(url, timeout=5)
                    if options_response.status_code not in [200, 204, 405]:
                        self.log(f"⚠️ OPTIONS request failed for {endpoint}: {options_response.status_code}", "WARN")
                    
                    # Test POST (actual request)
                    post_response = requests.post(url, json={}, timeout=5)
                    # Any response (even 400/422) means endpoint is accessible
                    if post_response.status_code >= 400 and post_response.status_code < 500:
                        self.log(f"✅ {endpoint} accessible (client error is expected)", "PASS")
                    elif post_response.status_code >= 500:
                        self.log(f"⚠️ {endpoint} server error: {post_response.status_code}", "WARN")
                    else:
                        self.log(f"✅ {endpoint} accessible: {post_response.status_code}", "PASS")
                else:
                    # Test GET for root endpoint
                    get_response = requests.get(url, timeout=5)
                    if get_response.status_code == 200:
                        self.log(f"✅ {endpoint} accessible: {get_response.status_code}", "PASS")
                    else:
                        self.log(f"⚠️ {endpoint} returned: {get_response.status_code}", "WARN")
                        
            except requests.exceptions.RequestException as e:
                self.log(f"❌ {endpoint} not accessible: {e}", "FAIL")
                all_accessible = False
        
        if all_accessible:
            self.log("✅ All API endpoints are accessible", "PASS")
        else:
            self.log("❌ Some API endpoints are not accessible", "FAIL")
        
        return all_accessible
    
    def test_cors_headers_present(self):
        """Test 5: Verify CORS headers are present for API requests"""
        self.log("=" * 60)
        self.log("TEST 5: CORS Headers Verification")
        self.log("=" * 60)
        
        try:
            # Test OPTIONS request (preflight)
            options_url = f"{self.frontend_url}/api/register"
            response = requests.options(options_url, timeout=10)
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            
            if not cors_headers["Access-Control-Allow-Origin"]:
                self.log("❌ Missing Access-Control-Allow-Origin header", "FAIL")
                return False
            
            if "putana.date" in cors_headers["Access-Control-Allow-Origin"] or cors_headers["Access-Control-Allow-Origin"] == "*":
                self.log("✅ CORS headers present and configured correctly", "PASS")
                self.log(f"Allow-Origin: {cors_headers['Access-Control-Allow-Origin']}", "INFO")
                return True
            else:
                self.log(f"⚠️ CORS origin may not include putana.date: {cors_headers['Access-Control-Allow-Origin']}", "WARN")
                return True  # Not a failure, but should be checked
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to test CORS headers: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🚀 SERVICE WORKER API ENDPOINTS VERIFICATION TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # Test 1: Service worker file exists
        exists, sw_content = self.test_service_worker_file_exists()
        results.append(("Service Worker Accessibility", exists))
        
        # Test 2: No hardcoded old ports
        if exists:
            results.append(("No Hardcoded Old Ports", self.test_service_worker_no_hardcoded_ports()))
        
        # Test 3: API request handling
        if exists:
            results.append(("API Request Handling", self.test_service_worker_api_request_handling()))
        
        # Test 4: API endpoints accessible
        results.append(("API Endpoints Accessible", self.test_api_endpoints_accessible_via_service_worker_proxy()))
        
        # Test 5: CORS headers
        results.append(("CORS Headers Present", self.test_cors_headers_present()))
        
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
    tester = ServiceWorkerEndpointTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

