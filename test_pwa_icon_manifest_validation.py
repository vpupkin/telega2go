#!/usr/bin/env python3
"""
Test Suite: PWA Icon and Manifest Resource Validation
Tests to ensure all PWA icons exist and manifest resources are properly configured.
"""

import requests
import json
import sys
import re
from urllib.parse import urljoin

class PWAIconManifestTest:
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
    
    def test_all_manifest_icons_exist(self):
        """Test 1: Verify all icons referenced in manifest actually exist"""
        self.log("=" * 60)
        self.log("TEST 1: Manifest Icons Existence Check")
        self.log("=" * 60)
        
        try:
            # Get manifest
            manifest_url = f"{self.frontend_url}/manifest.json"
            manifest_response = requests.get(manifest_url, timeout=10)
            manifest_response.raise_for_status()
            manifest = manifest_response.json()
            
            if "icons" not in manifest:
                self.log("❌ No icons defined in manifest", "FAIL")
                return False
            
            icons = manifest["icons"]
            if not isinstance(icons, list):
                self.log("❌ Icons field is not an array", "FAIL")
                return False
            
            self.log(f"Checking {len(icons)} icons from manifest", "INFO")
            
            all_icons_exist = True
            missing_icons = []
            
            for i, icon in enumerate(icons):
                if not isinstance(icon, dict) or "src" not in icon:
                    self.log(f"⚠️ Icon {i+1} is invalid", "WARN")
                    continue
                
                icon_src = icon["src"]
                icon_sizes = icon.get("sizes", "unknown")
                icon_type = icon.get("type", "unknown")
                
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
                            self.log(f"✅ Icon {icon_src} ({icon_sizes}) exists and is valid image", "PASS")
                        else:
                            self.log(f"❌ Icon {icon_src} exists but is not an image: {content_type}", "FAIL")
                            all_icons_exist = False
                    else:
                        self.log(f"❌ Icon {icon_src} not found: HTTP {icon_response.status_code}", "FAIL")
                        missing_icons.append(icon_src)
                        all_icons_exist = False
                        
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Icon {icon_src} failed to load: {e}", "FAIL")
                    missing_icons.append(icon_src)
                    all_icons_exist = False
            
            if missing_icons:
                self.log(f"❌ Missing icons: {missing_icons}", "FAIL")
            
            return all_icons_exist
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch manifest: {e}", "FAIL")
            return False
        except json.JSONDecodeError as e:
            self.log(f"❌ Manifest is not valid JSON: {e}", "FAIL")
            return False
    
    def test_common_pwa_icon_sizes(self):
        """Test 2: Verify common PWA icon sizes exist"""
        self.log("=" * 60)
        self.log("TEST 2: Common PWA Icon Sizes Check")
        self.log("=" * 60)
        
        # Common PWA icon sizes and filenames
        common_icons = [
            ("icon-192.png", "192x192"),
            ("icon-512.png", "512x512"),
            ("icon-144.png", "144x144"),  # This one was mentioned in the error
            ("icon-96.png", "96x96"),
            ("icon-72.png", "72x72"),
            ("icon-48.png", "48x48"),
            ("icon-36.png", "36x36"),
            ("icon-24.png", "24x24"),
            ("icon-16.png", "16x16")
        ]
        
        existing_icons = []
        missing_icons = []
        
        for icon_file, size in common_icons:
            icon_url = f"{self.frontend_url}/{icon_file}"
            
            try:
                icon_response = requests.head(icon_url, timeout=5)
                if icon_response.status_code == 200:
                    content_type = icon_response.headers.get("content-type", "")
                    if "image/" in content_type:
                        existing_icons.append((icon_file, size))
                        self.log(f"✅ {icon_file} ({size}) exists", "PASS")
                    else:
                        self.log(f"❌ {icon_file} exists but is not an image: {content_type}", "FAIL")
                        missing_icons.append(icon_file)
                else:
                    self.log(f"⚠️ {icon_file} not found: HTTP {icon_response.status_code}", "WARN")
                    missing_icons.append(icon_file)
                    
            except requests.exceptions.RequestException as e:
                self.log(f"⚠️ {icon_file} failed to load: {e}", "WARN")
                missing_icons.append(icon_file)
        
        # Check if we have the minimum required icons
        required_sizes = ["192x192", "512x512"]
        has_required = all(any(size in icon[1] for icon in existing_icons) for size in required_sizes)
        
        if has_required:
            self.log("✅ All required PWA icon sizes present", "PASS")
        else:
            self.log("❌ Missing required PWA icon sizes", "FAIL")
        
        self.log(f"Found {len(existing_icons)} icons, {len(missing_icons)} missing", "INFO")
        
        return has_required and len(existing_icons) >= 2
    
    def test_icon_file_integrity(self):
        """Test 3: Verify icon files are valid images"""
        self.log("=" * 60)
        self.log("TEST 3: Icon File Integrity Check")
        self.log("=" * 60)
        
        # Test the icons that were found to exist
        test_icons = ["icon-192.png", "icon-512.png", "icon-144.png"]
        
        all_valid = True
        
        for icon_file in test_icons:
            icon_url = f"{self.frontend_url}/{icon_file}"
            
            try:
                icon_response = requests.get(icon_url, timeout=10)
                if icon_response.status_code == 200:
                    content_type = icon_response.headers.get("content-type", "")
                    content_length = len(icon_response.content)
                    
                    if "image/" in content_type:
                        self.log(f"✅ {icon_file}: Valid image ({content_type}, {content_length} bytes)", "PASS")
                        
                        # Check if it's actually a valid image by checking magic bytes
                        if icon_response.content.startswith(b'\x89PNG'):
                            self.log(f"✅ {icon_file}: Valid PNG file", "PASS")
                        elif icon_response.content.startswith(b'\xff\xd8\xff'):
                            self.log(f"✅ {icon_file}: Valid JPEG file", "PASS")
                        else:
                            self.log(f"⚠️ {icon_file}: May not be a standard image format", "WARN")
                    else:
                        self.log(f"❌ {icon_file}: Not an image ({content_type})", "FAIL")
                        all_valid = False
                else:
                    self.log(f"❌ {icon_file}: HTTP {icon_response.status_code}", "FAIL")
                    all_valid = False
                    
            except requests.exceptions.RequestException as e:
                self.log(f"❌ {icon_file}: Failed to load ({e})", "FAIL")
                all_valid = False
        
        return all_valid
    
    def test_manifest_icon_references(self):
        """Test 4: Verify manifest references match actual files"""
        self.log("=" * 60)
        self.log("TEST 4: Manifest Icon References Check")
        self.log("=" * 60)
        
        try:
            # Get manifest
            manifest_url = f"{self.frontend_url}/manifest.json"
            manifest_response = requests.get(manifest_url, timeout=10)
            manifest_response.raise_for_status()
            manifest = manifest_response.json()
            
            if "icons" not in manifest:
                self.log("❌ No icons in manifest", "FAIL")
                return False
            
            icons = manifest["icons"]
            referenced_files = []
            
            for icon in icons:
                if isinstance(icon, dict) and "src" in icon:
                    icon_src = icon["src"]
                    if icon_src.startswith("/"):
                        referenced_files.append(icon_src[1:])  # Remove leading slash
                    else:
                        referenced_files.append(icon_src)
            
            self.log(f"Manifest references {len(referenced_files)} icon files", "INFO")
            
            # Check if referenced files exist
            missing_references = []
            for icon_file in referenced_files:
                icon_url = f"{self.frontend_url}/{icon_file}"
                try:
                    icon_response = requests.head(icon_url, timeout=5)
                    if icon_response.status_code != 200:
                        missing_references.append(icon_file)
                except:
                    missing_references.append(icon_file)
            
            if missing_references:
                self.log(f"❌ Manifest references missing files: {missing_references}", "FAIL")
                return False
            else:
                self.log("✅ All manifest icon references exist", "PASS")
            
            # Check for common icon files that might be missing from manifest
            common_files = ["icon-192.png", "icon-512.png", "icon-144.png"]
            manifest_files = [f for f in referenced_files if f in common_files]
            
            if len(manifest_files) >= 2:
                self.log("✅ Manifest includes common PWA icon files", "PASS")
            else:
                self.log(f"⚠️ Manifest may be missing common icon files (has {len(manifest_files)}/3)", "WARN")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch manifest: {e}", "FAIL")
            return False
        except json.JSONDecodeError as e:
            self.log(f"❌ Manifest is not valid JSON: {e}", "FAIL")
            return False
    
    def test_html_icon_references(self):
        """Test 5: Verify HTML references to icons are correct"""
        self.log("=" * 60)
        self.log("TEST 5: HTML Icon References Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Find all icon references in HTML
            icon_patterns = [
                r'href=["\']([^"\']*icon[^"\']*)["\']',
                r'src=["\']([^"\']*icon[^"\']*)["\']',
                r'content=["\']([^"\']*icon[^"\']*)["\']'
            ]
            
            html_icon_refs = []
            for pattern in icon_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                html_icon_refs.extend(matches)
            
            if not html_icon_refs:
                self.log("⚠️ No icon references found in HTML", "WARN")
                return True
            
            self.log(f"Found {len(html_icon_refs)} icon references in HTML", "INFO")
            
            # Check if referenced icons exist
            missing_html_refs = []
            for icon_ref in html_icon_refs:
                if icon_ref.startswith("/"):
                    icon_url = f"{self.frontend_url}{icon_ref}"
                else:
                    icon_url = urljoin(self.frontend_url, icon_ref)
                
                try:
                    icon_response = requests.head(icon_url, timeout=5)
                    if icon_response.status_code != 200:
                        missing_html_refs.append(icon_ref)
                except:
                    missing_html_refs.append(icon_ref)
            
            if missing_html_refs:
                self.log(f"❌ HTML references missing icons: {missing_html_refs}", "FAIL")
                return False
            else:
                self.log("✅ All HTML icon references exist", "PASS")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🚀 PWA ICON AND MANIFEST RESOURCE VALIDATION TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # Test 1: All manifest icons exist
        results.append(("Manifest Icons Existence", self.test_all_manifest_icons_exist()))
        
        # Test 2: Common PWA icon sizes
        results.append(("Common PWA Icon Sizes", self.test_common_pwa_icon_sizes()))
        
        # Test 3: Icon file integrity
        results.append(("Icon File Integrity", self.test_icon_file_integrity()))
        
        # Test 4: Manifest icon references
        results.append(("Manifest Icon References", self.test_manifest_icon_references()))
        
        # Test 5: HTML icon references
        results.append(("HTML Icon References", self.test_html_icon_references()))
        
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
    tester = PWAIconManifestTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

