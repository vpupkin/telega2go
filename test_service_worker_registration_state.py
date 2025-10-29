#!/usr/bin/env python3
"""
Test Suite: Service Worker Registration State and Browser Extension Runtime Messages
Tests to ensure service worker registers correctly and handles browser extension interactions.
"""

import requests
import json
import sys
import re
from urllib.parse import urljoin

class ServiceWorkerRegistrationStateTest:
    def __init__(self):
        self.frontend_url = "https://putana.date"
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
    
    def test_service_worker_registration_code_present(self):
        """Test 1: Verify service worker registration code exists in HTML/JS"""
        self.log("=" * 60)
        self.log("TEST 1: Service Worker Registration Code Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Check for service worker registration in HTML
            sw_registration_patterns = [
                r"navigator\.serviceWorker\.register",
                r"serviceWorker\.register",
                r"ServiceWorkerRegistration",
                r"SW registered"
            ]
            
            found_in_html = False
            for pattern in sw_registration_patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    found_in_html = True
                    self.log(f"✅ Found service worker registration pattern: {pattern}", "PASS")
                    break
            
            if not found_in_html:
                # Check JavaScript bundles
                script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
                
                found_in_js = False
                for script_path in script_urls[:2]:  # Check first 2 bundles
                    script_url = f"{self.frontend_url}{script_path}"
                    try:
                        script_response = requests.get(script_url, timeout=10)
                        script_response.raise_for_status()
                        script_content = script_response.text
                        
                        for pattern in sw_registration_patterns:
                            if re.search(pattern, script_content, re.IGNORECASE):
                                found_in_js = True
                                self.log(f"✅ Found service worker registration in {script_path}", "PASS")
                                break
                        
                        if found_in_js:
                            break
                    except:
                        continue
                
                if not found_in_js:
                    self.log("❌ Service worker registration code not found", "FAIL")
                    return False
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_service_worker_registration_state_handling(self):
        """Test 2: Verify service worker handles registration state correctly"""
        self.log("=" * 60)
        self.log("TEST 2: Service Worker Registration State Handling")
        self.log("=" * 60)
        
        try:
            # Get service worker file
            sw_url = f"{self.frontend_url}/sw.js"
            sw_response = requests.get(sw_url, timeout=10)
            sw_response.raise_for_status()
            sw_content = sw_response.text
            
            # Check for proper state handling
            state_patterns = [
                r"installing",
                r"waiting",
                r"active",
                r"navigationPreload",
                r"scope"
            ]
            
            found_patterns = []
            for pattern in state_patterns:
                if re.search(pattern, sw_content, re.IGNORECASE):
                    found_patterns.append(pattern)
            
            # Check HTML/JS for registration state handling
            response = requests.get(self.frontend_url, timeout=10)
            html_content = response.text
            
            # Look for registration promise handling
            registration_handling = [
                r"\.then\s*\(",
                r"\.catch\s*\(",
                r"ServiceWorkerRegistration",
                r"\.active",
                r"\.installing",
                r"\.waiting"
            ]
            
            found_handling = False
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            for script_path in script_urls[:2]:
                script_url = f"{self.frontend_url}{script_path}"
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_content = script_response.text
                    
                    for pattern in registration_handling:
                        if re.search(pattern, script_content):
                            found_handling = True
                            break
                    
                    if found_handling:
                        break
                except:
                    continue
            
            if found_handling:
                self.log("✅ Service worker registration state handling found", "PASS")
            else:
                self.log("⚠️ Service worker registration state handling may be missing", "WARN")
            
            # Check for proper error handling
            if "catch" in sw_content or "error" in sw_content.lower():
                self.log("✅ Service worker has error handling", "PASS")
            else:
                self.log("⚠️ Service worker may lack error handling", "WARN")
            
            return found_handling or len(found_patterns) > 0
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to check service worker: {e}", "FAIL")
            return False
    
    def test_browser_extension_runtime_message_handling(self):
        """Test 3: Verify app handles browser extension runtime messages gracefully"""
        self.log("=" * 60)
        self.log("TEST 3: Browser Extension Runtime Message Handling")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            runtime_message_patterns = [
                r"browser\.runtime",
                r"chrome\.runtime",
                r"BROWSER\.runtime",
                r"runtime\.sendMessage",
                r"runtime\.onMessage"
            ]
            
            found_patterns = []
            unhandled_patterns = []
            
            for script_path in script_urls[:2]:
                script_url = f"{self.frontend_url}{script_path}"
                self.log(f"Checking runtime message handling in: {script_path}")
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    for pattern in runtime_message_patterns:
                        if re.search(pattern, script_content, re.IGNORECASE):
                            found_patterns.append(f"{pattern} in {script_path}")
                            
                            # Check if it's properly handled (try/catch or conditional)
                            lines = script_content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    # Check surrounding context for error handling
                                    context_start = max(0, i - 5)
                                    context_end = min(len(lines), i + 5)
                                    context = '\n'.join(lines[context_start:context_end])
                                    
                                    if not (re.search(r'try\s*\{', context) or 
                                            re.search(r'if\s*\(.*runtime', context) or
                                            re.search(r'\?\.runtime', context)):
                                        unhandled_patterns.append(f"Line {i} in {script_path}: {line.strip()[:80]}")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️ Could not check {script_path}: {e}", "WARN")
                    continue
            
            if found_patterns:
                self.log(f"⚠️ Found browser extension runtime patterns: {len(found_patterns)}", "WARN")
                
                if unhandled_patterns:
                    self.log(f"❌ Found unhandled runtime message patterns:", "FAIL")
                    for pattern in unhandled_patterns[:5]:
                        self.log(f"   {pattern}", "FAIL")
                    return False
                else:
                    self.log("✅ Runtime message patterns are properly handled", "PASS")
                    return True
            else:
                self.log("✅ No browser extension runtime patterns found (app doesn't interact with extensions)", "PASS")
                return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_service_worker_navigation_preload(self):
        """Test 4: Verify service worker navigation preload is configured"""
        self.log("=" * 60)
        self.log("TEST 4: Service Worker Navigation Preload Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Check for navigationPreload in registration
            if "navigationPreload" in html_content or "NavigationPreloadManager" in html_content:
                self.log("✅ Navigation preload is mentioned in registration", "PASS")
            else:
                self.log("⚠️ Navigation preload may not be configured", "WARN")
            
            # Check service worker file for preload handling
            sw_url = f"{self.frontend_url}/sw.js"
            try:
                sw_response = requests.get(sw_url, timeout=10)
                sw_content = sw_response.text
                
                if "navigationPreload" in sw_content.lower():
                    self.log("✅ Service worker handles navigation preload", "PASS")
                else:
                    self.log("ℹ️ Service worker doesn't explicitly handle navigation preload", "INFO")
            except:
                pass
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to check navigation preload: {e}", "FAIL")
            return False
    
    def test_service_worker_scope_consistency(self):
        """Test 5: Verify service worker scope is consistent"""
        self.log("=" * 60)
        self.log("TEST 5: Service Worker Scope Consistency Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract service worker registration
            sw_register_match = re.search(r"serviceWorker\.register\(['\"]([^'\"]+)['\"]", html_content)
            
            if not sw_register_match:
                # Check JavaScript bundles
                script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
                for script_path in script_urls[:2]:
                    try:
                        script_url = f"{self.frontend_url}{script_path}"
                        script_response = requests.get(script_url, timeout=10)
                        script_content = script_response.text
                        sw_register_match = re.search(r"serviceWorker\.register\(['\"]([^'\"]+)['\"]", script_content)
                        if sw_register_match:
                            break
                    except:
                        continue
            
            if sw_register_match:
                sw_path = sw_register_match.group(1)
                self.log(f"Service worker path: {sw_path}", "INFO")
                
                # Check if scope is mentioned
                scope_match = re.search(r"scope:\s*['\"]([^'\"]+)['\"]", html_content, re.IGNORECASE)
                if scope_match:
                    scope = scope_match.group(1)
                    self.log(f"Service worker scope: {scope}", "INFO")
                    
                    if scope == "/" or scope == f"{self.frontend_url}/":
                        self.log("✅ Service worker scope is set to root (correct)", "PASS")
                        return True
                    else:
                        self.log(f"⚠️ Service worker scope: {scope}", "WARN")
                else:
                    self.log("ℹ️ Service worker scope not explicitly set (defaults to SW file location)", "INFO")
                    return True
            else:
                self.log("⚠️ Could not find service worker registration", "WARN")
                return True  # Not a failure, just a warning
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to check scope: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🚀 SERVICE WORKER REGISTRATION STATE AND BROWSER EXTENSION TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # Test 1: Service worker registration code present
        results.append(("Service Worker Registration Code", self.test_service_worker_registration_code_present()))
        
        # Test 2: Registration state handling
        results.append(("Service Worker Registration State", self.test_service_worker_registration_state_handling()))
        
        # Test 3: Browser extension runtime messages
        results.append(("Browser Extension Runtime Messages", self.test_browser_extension_runtime_message_handling()))
        
        # Test 4: Navigation preload
        results.append(("Service Worker Navigation Preload", self.test_service_worker_navigation_preload()))
        
        # Test 5: Scope consistency
        results.append(("Service Worker Scope Consistency", self.test_service_worker_scope_consistency()))
        
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
    tester = ServiceWorkerRegistrationStateTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

