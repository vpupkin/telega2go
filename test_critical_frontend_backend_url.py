#!/usr/bin/env python3
"""
Test Suite: CRITICAL Frontend Backend URL Configuration Penalty Test
This test catches the most critical error: frontend still using old port 5572!
"""

import requests
import json
import sys
import re
from urllib.parse import urljoin

class CriticalFrontendBackendURLTest:
    def __init__(self):
        self.frontend_url = "https://putana.date"
        self.old_port = "5572"
        self.new_port = "55552"
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Log test messages"""
        prefix = {
            "INFO": "ℹ️",
            "PASS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️",
            "CRITICAL": "🚨"
        }.get(level, "ℹ️")
        print(f"{prefix} {message}")
        self.test_results.append({"level": level, "message": message})
    
    def test_critical_old_port_5572_elimination(self):
        """CRITICAL TEST: Verify NO references to old port 5572 exist"""
        self.log("=" * 60)
        self.log("🚨 CRITICAL TEST: Old Port 5572 Elimination Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract ALL JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            if not script_urls:
                self.log("❌ No JavaScript bundles found", "FAIL")
                return False
            
            critical_errors = []
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                self.log(f"🚨 CRITICAL CHECK: {script_path}")
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # CRITICAL: Check for ANY reference to old port 5572
                    old_port_patterns = [
                        f"localhost:{self.old_port}",
                        f":{self.old_port}",
                        f"127.0.0.1:{self.old_port}",
                        f"http://localhost:{self.old_port}",
                        f"https://localhost:{self.old_port}",
                        f"http://127.0.0.1:{self.old_port}",
                        f"https://127.0.0.1:{self.old_port}",
                        f"putana.date:{self.old_port}",
                        f"https://putana.date:{self.old_port}",
                        f"http://putana.date:{self.old_port}"
                    ]
                    
                    for pattern in old_port_patterns:
                        if pattern in script_content:
                            # Find line numbers
                            lines = script_content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if pattern in line:
                                    critical_errors.append(f"🚨 CRITICAL: {pattern} found in {script_path} line {i}: {line.strip()[:100]}")
                    
                    # Check for specific error patterns from the console
                    error_patterns = [
                        f"POST https://putana.date:{self.old_port}/api/register",
                        f"POST http://localhost:{self.old_port}/api/",
                        f"fetch.*{self.old_port}",
                        f"axios.*{self.old_port}",
                        f"XMLHttpRequest.*{self.old_port}"
                    ]
                    
                    for pattern in error_patterns:
                        if re.search(pattern, script_content, re.IGNORECASE):
                            critical_errors.append(f"🚨 CRITICAL: API call pattern {pattern} found in {script_path}")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ CRITICAL: Could not check {script_path}: {e}", "FAIL")
                    critical_errors.append(f"🚨 CRITICAL: Failed to check {script_path}")
                    continue
            
            if critical_errors:
                self.log(f"🚨 CRITICAL FAILURE: Found {len(critical_errors)} old port references!", "CRITICAL")
                for error in critical_errors[:10]:  # Show first 10
                    self.log(error, "CRITICAL")
                return False
            else:
                self.log("✅ CRITICAL: No old port 5572 references found", "PASS")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ CRITICAL: Failed to fetch frontend: {e}", "FAIL")
            return False
    
    def test_new_port_55552_usage(self):
        """CRITICAL TEST: Verify new port 55552 is being used"""
        self.log("=" * 60)
        self.log("🚨 CRITICAL TEST: New Port 55552 Usage Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            new_port_found = False
            new_port_patterns = [
                f"putana.date/api",
                f"https://putana.date/api",
                f"putana.date/otp",
                f"https://putana.date/otp",
                f"/api/",
                f"/otp/"
            ]
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    for pattern in new_port_patterns:
                        if pattern in script_content:
                            new_port_found = True
                            self.log(f"✅ Found new port usage: {pattern} in {script_path}", "PASS")
                            break
                    
                    if new_port_found:
                        break
                        
                except requests.exceptions.RequestException as e:
                    continue
            
            if not new_port_found:
                self.log("❌ CRITICAL: No new port 55552 usage found!", "FAIL")
                return False
            else:
                self.log("✅ CRITICAL: New port 55552 is being used", "PASS")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ CRITICAL: Failed to check new port usage: {e}", "FAIL")
            return False
    
    def test_api_endpoint_connectivity(self):
        """CRITICAL TEST: Verify API endpoints are actually reachable"""
        self.log("=" * 60)
        self.log("🚨 CRITICAL TEST: API Endpoint Connectivity Check")
        self.log("=" * 60)
        
        api_endpoints = [
            f"{self.frontend_url}/api/",
            f"{self.frontend_url}/api/register",
            f"{self.frontend_url}/api/verify-otp",
            f"{self.frontend_url}/api/resend-otp",
            f"{self.frontend_url}/api/verify-magic-link"
        ]
        
        all_reachable = True
        
        for endpoint in api_endpoints:
            try:
                # Test OPTIONS first (preflight)
                options_response = requests.options(endpoint, timeout=5)
                if options_response.status_code not in [200, 204, 405]:
                    self.log(f"❌ CRITICAL: OPTIONS failed for {endpoint}: {options_response.status_code}", "FAIL")
                    all_reachable = False
                else:
                    self.log(f"✅ OPTIONS working for {endpoint}", "PASS")
                
                # Test actual endpoint
                if "register" in endpoint or "verify-otp" in endpoint or "resend-otp" in endpoint or "verify-magic-link" in endpoint:
                    # These need POST
                    post_response = requests.post(endpoint, json={}, timeout=5)
                    if post_response.status_code >= 500:
                        self.log(f"❌ CRITICAL: Server error for {endpoint}: {post_response.status_code}", "FAIL")
                        all_reachable = False
                    elif post_response.status_code >= 400:
                        self.log(f"✅ {endpoint} reachable (client error expected): {post_response.status_code}", "PASS")
                    else:
                        self.log(f"✅ {endpoint} reachable: {post_response.status_code}", "PASS")
                else:
                    # GET for root endpoint
                    get_response = requests.get(endpoint, timeout=5)
                    if get_response.status_code == 200:
                        self.log(f"✅ {endpoint} reachable: {get_response.status_code}", "PASS")
                    else:
                        self.log(f"❌ CRITICAL: {endpoint} not reachable: {get_response.status_code}", "FAIL")
                        all_reachable = False
                        
            except requests.exceptions.Timeout:
                self.log(f"❌ CRITICAL: Timeout for {endpoint} - CONNECTION TIMED OUT!", "FAIL")
                all_reachable = False
            except requests.exceptions.ConnectionError:
                self.log(f"❌ CRITICAL: Connection error for {endpoint} - CONNECTION REFUSED!", "FAIL")
                all_reachable = False
            except requests.exceptions.RequestException as e:
                self.log(f"❌ CRITICAL: Request failed for {endpoint}: {e}", "FAIL")
                all_reachable = False
        
        return all_reachable
    
    def run_all_tests(self):
        """Run all CRITICAL tests"""
        print("\n" + "=" * 60)
        print("🚨 CRITICAL FRONTEND BACKEND URL CONFIGURATION PENALTY TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # CRITICAL Test 1: No old port 5572
        results.append(("CRITICAL: No Old Port 5572", self.test_critical_old_port_5572_elimination()))
        
        # CRITICAL Test 2: New port 55552 usage
        results.append(("CRITICAL: New Port 55552 Usage", self.test_new_port_55552_usage()))
        
        # CRITICAL Test 3: API connectivity
        results.append(("CRITICAL: API Endpoint Connectivity", self.test_api_endpoint_connectivity()))
        
        # Summary
        print("\n" + "=" * 60)
        print("🚨 CRITICAL TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "🚨 CRITICAL FAIL"
            print(f"{status}: {test_name}")
        
        print("\n" + "=" * 60)
        print(f"🚨 CRITICAL Results: {passed}/{total} tests passed")
        if passed < total:
            print("🚨 PENALTY: CRITICAL ISSUES FOUND - FRONTEND STILL USING OLD PORT!")
        print("=" * 60 + "\n")
        
        return passed == total

if __name__ == "__main__":
    tester = CriticalFrontendBackendURLTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

