#!/usr/bin/env python3
"""
Test Suite: PWA Manifest and Service Worker Registration Verification
Tests to ensure PWA manifest is valid and service worker registers correctly.
"""

import requests
import json
import sys
from urllib.parse import urljoin

class PWAManifestTest:
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
    
    def test_manifest_file_exists_and_valid(self):
        """Test 1: Verify PWA manifest file exists and is valid JSON"""
        self.log("=" * 60)
        self.log("TEST 1: PWA Manifest File Validation")
        self.log("=" * 60)
        
        try:
            manifest_url = f"{self.frontend_url}/manifest.json"
            response = requests.get(manifest_url, timeout=10)
            response.raise_for_status()
            
            # Check if it's valid JSON
            try:
                manifest = response.json()
                self.log("✅ Manifest file exists and is valid JSON", "PASS")
                return True, manifest
            except json.JSONDecodeError as e:
                self.log(f"❌ Manifest file is not valid JSON: {e}", "FAIL")
                return False, None
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch manifest: {e}", "FAIL")
            return False, None
    
    def test_manifest_required_fields(self):
        """Test 2: Verify manifest has required PWA fields"""
        self.log("=" * 60)
        self.log("TEST 2: PWA Manifest Required Fields")
        self.log("=" * 60)
        
        try:
            manifest_url = f"{self.frontend_url}/manifest.json"
            response = requests.get(manifest_url, timeout=10)
            response.raise_for_status()
            manifest = response.json()
            
            required_fields = [
                "name",
                "short_name", 
                "start_url",
                "display",
                "icons"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in manifest:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log(f"❌ Missing required fields: {missing_fields}", "FAIL")
                return False
            
            self.log("✅ All required PWA fields present", "PASS")
            
            # Check specific values
            if manifest.get("name") == "Telega2Go - User Registration":
                self.log("✅ App name is correct", "PASS")
            else:
                self.log(f"⚠️ App name: {manifest.get('name')}", "WARN")
            
            if manifest.get("display") in ["standalone", "fullscreen", "minimal-ui"]:
                self.log("✅ Display mode is appropriate for PWA", "PASS")
            else:
                self.log(f"⚠️ Display mode: {manifest.get('display')}", "WARN")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch manifest: {e}", "FAIL")
            return False
        except json.JSONDecodeError as e:
            self.log(f"❌ Manifest is not valid JSON: {e}", "FAIL")
            return False
    
    def test_manifest_icons_exist(self):
        """Test 3: Verify all manifest icons exist and are accessible"""
        self.log("=" * 60)
        self.log("TEST 3: PWA Manifest Icons Accessibility")
        self.log("=" * 60)
        
        try:
            manifest_url = f"{self.frontend_url}/manifest.json"
            response = requests.get(manifest_url, timeout=10)
            response.raise_for_status()
            manifest = response.json()
            
            if "icons" not in manifest:
                self.log("❌ No icons defined in manifest", "FAIL")
                return False
            
            icons = manifest["icons"]
            if not isinstance(icons, list) or len(icons) == 0:
                self.log("❌ Icons field is not a valid array", "FAIL")
                return False
            
            self.log(f"Found {len(icons)} icon definitions", "INFO")
            
            all_icons_accessible = True
            required_sizes = ["192", "512"]  # Common PWA icon sizes
            
            for icon in icons:
                if not isinstance(icon, dict) or "src" not in icon:
                    self.log("⚠️ Invalid icon definition", "WARN")
                    continue
                
                icon_src = icon["src"]
                icon_size = icon.get("sizes", "unknown")
                
                # Make URL absolute
                if icon_src.startswith("/"):
                    icon_url = f"{self.frontend_url}{icon_src}"
                else:
                    icon_url = urljoin(self.frontend_url, icon_src)
                
                try:
                    icon_response = requests.head(icon_url, timeout=5)
                    if icon_response.status_code == 200:
                        content_type = icon_response.headers.get("content-type", "")
                        if "image/" in content_type:
                            self.log(f"✅ Icon {icon_src} ({icon_size}) accessible", "PASS")
                        else:
                            self.log(f"⚠️ Icon {icon_src} not an image: {content_type}", "WARN")
                    else:
                        self.log(f"❌ Icon {icon_src} not accessible: {icon_response.status_code}", "FAIL")
                        all_icons_accessible = False
                        
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Icon {icon_src} failed to load: {e}", "FAIL")
                    all_icons_accessible = False
            
            # Check for specific missing icon mentioned in error
            missing_icon = f"{self.frontend_url}/icon-144.png"
            try:
                missing_response = requests.head(missing_icon, timeout=5)
                if missing_response.status_code == 200:
                    self.log("✅ icon-144.png exists (was mentioned in error)", "PASS")
                else:
                    self.log(f"⚠️ icon-144.png missing: {missing_response.status_code}", "WARN")
            except:
                self.log("⚠️ icon-144.png not found (may be referenced but not exist)", "WARN")
            
            return all_icons_accessible
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch manifest: {e}", "FAIL")
            return False
        except json.JSONDecodeError as e:
            self.log(f"❌ Manifest is not valid JSON: {e}", "FAIL")
            return False
    
    def test_service_worker_registration_in_html(self):
        """Test 4: Verify service worker registration code in HTML"""
        self.log("=" * 60)
        self.log("TEST 4: Service Worker Registration Code")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Check for service worker registration
            sw_patterns = [
                r"navigator\.serviceWorker\.register",
                r"serviceWorker\.register",
                r"/sw\.js",
                r"ServiceWorker"
            ]
            
            found_patterns = []
            for pattern in sw_patterns:
                if pattern in html_content:
                    found_patterns.append(pattern)
            
            if not found_patterns:
                self.log("❌ No service worker registration found in HTML", "FAIL")
                return False
            
            self.log("✅ Service worker registration code found in HTML", "PASS")
            
            # Check for proper registration
            if "navigator.serviceWorker.register" in html_content:
                self.log("✅ Uses navigator.serviceWorker.register", "PASS")
            else:
                self.log("⚠️ May not use standard service worker registration", "WARN")
            
            # Check for error handling
            if "catch" in html_content and "serviceWorker" in html_content:
                self.log("✅ Service worker registration has error handling", "PASS")
            else:
                self.log("⚠️ Service worker registration may lack error handling", "WARN")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_service_worker_scope_and_scope_consistency(self):
        """Test 5: Verify service worker scope and consistency"""
        self.log("=" * 60)
        self.log("TEST 5: Service Worker Scope Verification")
        self.log("=" * 60)
        
        try:
            # Check HTML for service worker registration
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract service worker registration details
            import re
            sw_register_match = re.search(r"serviceWorker\.register\(['\"]([^'\"]+)['\"]", html_content)
            
            if not sw_register_match:
                self.log("❌ Could not find service worker registration in HTML", "FAIL")
                return False
            
            sw_path = sw_register_match.group(1)
            self.log(f"Service worker path: {sw_path}", "INFO")
            
            # Check if service worker file exists
            if sw_path.startswith("/"):
                sw_url = f"{self.frontend_url}{sw_path}"
            else:
                sw_url = urljoin(self.frontend_url, sw_path)
            
            try:
                sw_response = requests.get(sw_url, timeout=10)
                if sw_response.status_code == 200:
                    self.log("✅ Service worker file accessible", "PASS")
                else:
                    self.log(f"❌ Service worker file not accessible: {sw_response.status_code}", "FAIL")
                    return False
            except requests.exceptions.RequestException as e:
                self.log(f"❌ Service worker file failed to load: {e}", "FAIL")
                return False
            
            # Check scope (should be root "/")
            if "scope: 'https://putana.date/'" in html_content or "scope: \"https://putana.date/\"" in html_content:
                self.log("✅ Service worker scope is correctly set to root", "PASS")
            else:
                self.log("⚠️ Service worker scope may not be explicitly set (defaults to SW file location)", "WARN")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🚀 PWA MANIFEST AND SERVICE WORKER REGISTRATION TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # Test 1: Manifest file exists and valid
        exists, manifest = self.test_manifest_file_exists_and_valid()
        results.append(("Manifest File Valid", exists))
        
        # Test 2: Required fields
        if exists:
            results.append(("Required Fields Present", self.test_manifest_required_fields()))
        
        # Test 3: Icons accessible
        if exists:
            results.append(("Icons Accessible", self.test_manifest_icons_exist()))
        
        # Test 4: Service worker registration
        results.append(("Service Worker Registration", self.test_service_worker_registration_in_html()))
        
        # Test 5: Service worker scope
        results.append(("Service Worker Scope", self.test_service_worker_scope_and_scope_consistency()))
        
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
    tester = PWAManifestTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

