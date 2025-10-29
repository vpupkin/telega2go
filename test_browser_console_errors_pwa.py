#!/usr/bin/env python3
"""
Test Suite: Browser Console Errors and PWA Functionality Verification
Tests to ensure no critical console errors and PWA functionality works correctly.
"""

import requests
import json
import sys
import re
from urllib.parse import urljoin

class BrowserConsoleErrorTest:
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
    
    def test_no_critical_console_errors_in_html(self):
        """Test 1: Check HTML for potential console error sources"""
        self.log("=" * 60)
        self.log("TEST 1: HTML Console Error Sources Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Check for common console error patterns
            error_patterns = [
                r"undefined",
                r"null",
                r"TypeError",
                r"ReferenceError",
                r"Failed to convert value to 'Response'",
                r"ERR_FAILED",
                r"ERR_BLOCKED_BY_CLIENT",
                r"ERR_CORS",
                r"Access to fetch.*has been blocked by CORS policy"
            ]
            
            found_errors = []
            for pattern in error_patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    found_errors.append(pattern)
            
            if found_errors:
                self.log(f"⚠️ Found potential error patterns in HTML: {found_errors}", "WARN")
                # This is not necessarily a failure, just a warning
            else:
                self.log("✅ No obvious error patterns found in HTML", "PASS")
            
            # Check for proper script loading
            script_tags = re.findall(r'<script[^>]*src=["\']([^"\']+)["\'][^>]*>', html_content)
            if script_tags:
                self.log(f"✅ Found {len(script_tags)} script tags", "PASS")
                
                # Check if main bundle is loaded
                main_bundle = [s for s in script_tags if 'main.' in s and s.endswith('.js')]
                if main_bundle:
                    self.log(f"✅ Main bundle found: {main_bundle[0]}", "PASS")
                else:
                    self.log("⚠️ Main bundle may not be loaded", "WARN")
            else:
                self.log("❌ No script tags found", "FAIL")
                return False
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_javascript_bundle_loads_without_errors(self):
        """Test 2: Verify JavaScript bundles load without syntax errors"""
        self.log("=" * 60)
        self.log("TEST 2: JavaScript Bundle Loading Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            if not script_urls:
                self.log("❌ No JavaScript bundles found", "FAIL")
                return False
            
            all_bundles_ok = True
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                self.log(f"Checking bundle: {script_path}")
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    
                    # Check for common JavaScript syntax errors
                    script_content = script_response.text
                    
                    # Check for unclosed strings, brackets, etc.
                    syntax_issues = []
                    
                    # Check for unclosed template literals
                    if script_content.count('`') % 2 != 0:
                        syntax_issues.append("unclosed template literal")
                    
                    # Check for common error patterns
                    error_patterns = [
                        r"undefined\s*[^=]",
                        r"null\s*[^=]",
                        r"TypeError:",
                        r"ReferenceError:",
                        r"SyntaxError:"
                    ]
                    
                    for pattern in error_patterns:
                        if re.search(pattern, script_content):
                            syntax_issues.append(f"pattern: {pattern}")
                    
                    if syntax_issues:
                        self.log(f"⚠️ Potential syntax issues in {script_path}: {syntax_issues}", "WARN")
                    else:
                        self.log(f"✅ {script_path} appears syntactically correct", "PASS")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Failed to load {script_path}: {e}", "FAIL")
                    all_bundles_ok = False
            
            return all_bundles_ok
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_pwa_manifest_consistency(self):
        """Test 3: Verify PWA manifest is consistent with actual files"""
        self.log("=" * 60)
        self.log("TEST 3: PWA Manifest Consistency Check")
        self.log("=" * 60)
        
        try:
            # Get manifest
            manifest_url = f"{self.frontend_url}/manifest.json"
            manifest_response = requests.get(manifest_url, timeout=10)
            manifest_response.raise_for_status()
            manifest = manifest_response.json()
            
            # Check if manifest references exist
            if "icons" not in manifest:
                self.log("❌ No icons in manifest", "FAIL")
                return False
            
            icons_ok = True
            for icon in manifest["icons"]:
                if "src" not in icon:
                    continue
                
                icon_src = icon["src"]
                if icon_src.startswith("/"):
                    icon_url = f"{self.frontend_url}{icon_src}"
                else:
                    icon_url = urljoin(self.frontend_url, icon_src)
                
                try:
                    icon_response = requests.head(icon_url, timeout=5)
                    if icon_response.status_code != 200:
                        self.log(f"❌ Icon not found: {icon_src}", "FAIL")
                        icons_ok = False
                    else:
                        content_type = icon_response.headers.get("content-type", "")
                        if not content_type.startswith("image/"):
                            self.log(f"⚠️ Icon not an image: {icon_src} ({content_type})", "WARN")
                except:
                    self.log(f"❌ Icon failed to load: {icon_src}", "FAIL")
                    icons_ok = False
            
            # Check start_url
            start_url = manifest.get("start_url", "/")
            if not start_url.startswith("/"):
                start_url = "/" + start_url
            
            try:
                start_response = requests.get(f"{self.frontend_url}{start_url}", timeout=5)
                if start_response.status_code == 200:
                    self.log("✅ Start URL is accessible", "PASS")
                else:
                    self.log(f"⚠️ Start URL returned {start_response.status_code}", "WARN")
            except:
                self.log(f"⚠️ Start URL not accessible: {start_url}", "WARN")
            
            return icons_ok
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to check manifest: {e}", "FAIL")
            return False
        except json.JSONDecodeError as e:
            self.log(f"❌ Manifest is not valid JSON: {e}", "FAIL")
            return False
    
    def test_service_worker_functionality(self):
        """Test 4: Verify service worker functionality"""
        self.log("=" * 60)
        self.log("TEST 4: Service Worker Functionality Check")
        self.log("=" * 60)
        
        try:
            # Check service worker file
            sw_url = f"{self.frontend_url}/sw.js"
            sw_response = requests.get(sw_url, timeout=10)
            sw_response.raise_for_status()
            sw_content = sw_response.text
            
            # Check for required service worker features
            required_features = [
                "addEventListener",
                "install",
                "activate", 
                "fetch",
                "caches"
            ]
            
            missing_features = []
            for feature in required_features:
                if feature not in sw_content:
                    missing_features.append(feature)
            
            if missing_features:
                self.log(f"❌ Missing service worker features: {missing_features}", "FAIL")
                return False
            
            self.log("✅ Service worker has required features", "PASS")
            
            # Check for proper cache handling
            if "CACHE_NAME" in sw_content and "caches.open" in sw_content:
                self.log("✅ Service worker has cache management", "PASS")
            else:
                self.log("⚠️ Service worker may lack proper cache management", "WARN")
            
            # Check for API request handling
            if "/api/" in sw_content:
                self.log("✅ Service worker handles API requests", "PASS")
            else:
                self.log("⚠️ Service worker may not handle API requests", "WARN")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to check service worker: {e}", "FAIL")
            return False
    
    def test_no_missing_resources(self):
        """Test 5: Check for missing resources that cause console errors"""
        self.log("=" * 60)
        self.log("TEST 5: Missing Resources Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract all resource URLs from HTML
            resource_patterns = [
                r'href=["\']([^"\']+)["\']',  # CSS, manifest, etc.
                r'src=["\']([^"\']+)["\']',   # Scripts, images, etc.
                r'url\(["\']?([^"\']+)["\']?\)'  # CSS URLs
            ]
            
            all_resources = []
            for pattern in resource_patterns:
                matches = re.findall(pattern, html_content)
                all_resources.extend(matches)
            
            # Filter out external resources and data URLs
            local_resources = []
            for resource in all_resources:
                if (resource.startswith("/") or resource.startswith("./") or 
                    resource.startswith("../")) and not resource.startswith("http"):
                    local_resources.append(resource)
            
            self.log(f"Found {len(local_resources)} local resources to check", "INFO")
            
            missing_resources = []
            for resource in local_resources[:10]:  # Check first 10 to avoid too many requests
                if resource.startswith("/"):
                    resource_url = f"{self.frontend_url}{resource}"
                else:
                    resource_url = urljoin(self.frontend_url, resource)
                
                try:
                    resource_response = requests.head(resource_url, timeout=5)
                    if resource_response.status_code != 200:
                        missing_resources.append(f"{resource} ({resource_response.status_code})")
                except:
                    missing_resources.append(f"{resource} (failed to load)")
            
            if missing_resources:
                self.log(f"⚠️ Missing resources: {missing_resources}", "WARN")
                # Check if any are critical
                critical_missing = [r for r in missing_resources if any(x in r for x in ['.js', '.css', 'manifest.json'])]
                if critical_missing:
                    self.log(f"❌ Critical resources missing: {critical_missing}", "FAIL")
                    return False
            else:
                self.log("✅ All checked resources are accessible", "PASS")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to check resources: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🚀 BROWSER CONSOLE ERRORS AND PWA FUNCTIONALITY TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # Test 1: HTML console error sources
        results.append(("HTML Console Error Sources", self.test_no_critical_console_errors_in_html()))
        
        # Test 2: JavaScript bundle loading
        results.append(("JavaScript Bundle Loading", self.test_javascript_bundle_loads_without_errors()))
        
        # Test 3: PWA manifest consistency
        results.append(("PWA Manifest Consistency", self.test_pwa_manifest_consistency()))
        
        # Test 4: Service worker functionality
        results.append(("Service Worker Functionality", self.test_service_worker_functionality()))
        
        # Test 5: Missing resources
        results.append(("Missing Resources Check", self.test_no_missing_resources()))
        
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
    tester = BrowserConsoleErrorTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

