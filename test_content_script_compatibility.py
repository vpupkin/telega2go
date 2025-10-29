#!/usr/bin/env python3
"""
Test Suite: Content Script and Browser Extension Compatibility
Tests to ensure the app works correctly with browser extensions and content scripts.
"""

import requests
import json
import sys
import re
from urllib.parse import urljoin

class ContentScriptCompatibilityTest:
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
    
    def test_no_content_script_conflicts(self):
        """Test 1: Verify no conflicts with content scripts"""
        self.log("=" * 60)
        self.log("TEST 1: Content Script Conflicts Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Check for content script related patterns that might cause issues
            content_script_patterns = [
                r"content-script\.js",
                r"browser\.runtime\.sendMessage",
                r"chrome\.runtime\.sendMessage",
                r"StopNotification",
                r"BROWSER\.runtime"
            ]
            
            found_patterns = []
            for pattern in content_script_patterns:
                if re.search(pattern, html_content, re.IGNORECASE):
                    found_patterns.append(pattern)
            
            if found_patterns:
                self.log(f"⚠️ Found content script related patterns: {found_patterns}", "WARN")
                self.log("These may be from browser extensions, not the app itself", "INFO")
            else:
                self.log("✅ No content script patterns found in HTML", "PASS")
            
            # Check for proper script isolation
            if "use strict" in html_content:
                self.log("✅ App uses strict mode (good for isolation)", "PASS")
            else:
                self.log("⚠️ App may not use strict mode", "WARN")
            
            # Check for proper namespace usage
            if "window." in html_content and "var " in html_content:
                self.log("⚠️ App may pollute global namespace", "WARN")
            else:
                self.log("✅ App appears to use proper namespace isolation", "PASS")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_console_output_handling(self):
        """Test 2: Verify console output doesn't cause errors"""
        self.log("=" * 60)
        self.log("TEST 2: Console Output Handling Check")
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
            
            console_issues = []
            
            for script_path in script_urls[:2]:  # Check first 2 bundles
                script_url = f"{self.frontend_url}{script_path}"
                self.log(f"Checking console output in: {script_path}")
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # Check for problematic console patterns
                    problematic_patterns = [
                        r"console\.log\(undefined\)",
                        r"console\.log\(null\)",
                        r"console\.log\(false\)",
                        r"console\.log\(\{\}\)",
                        r"console\.log\(.*StopNotification.*\)",
                        r"console\.log\(.*BROWSER\.runtime.*\)"
                    ]
                    
                    for pattern in problematic_patterns:
                        if re.search(pattern, script_content):
                            console_issues.append(f"Pattern in {script_path}: {pattern}")
                    
                    # Check for proper console error handling
                    if "console.error" in script_content and "try" in script_content:
                        self.log(f"✅ {script_path} has proper error handling", "PASS")
                    elif "console.log" in script_content:
                        self.log(f"⚠️ {script_path} uses console.log but may lack error handling", "WARN")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️ Could not check {script_path}: {e}", "WARN")
                    continue
            
            if console_issues:
                self.log(f"⚠️ Found potentially problematic console output:", "WARN")
                for issue in console_issues[:5]:  # Show first 5
                    self.log(f"   {issue}", "WARN")
            else:
                self.log("✅ No problematic console output patterns found", "PASS")
            
            return len(console_issues) == 0
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_browser_extension_compatibility(self):
        """Test 3: Verify compatibility with browser extensions"""
        self.log("=" * 60)
        self.log("TEST 3: Browser Extension Compatibility Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Check for proper CSP headers (if any)
            csp_header = response.headers.get("Content-Security-Policy", "")
            if csp_header:
                self.log(f"✅ Content Security Policy present: {csp_header[:50]}...", "PASS")
            else:
                self.log("⚠️ No Content Security Policy (may allow extension conflicts)", "WARN")
            
            # Check for proper script loading order
            script_tags = re.findall(r'<script[^>]*>', html_content)
            if len(script_tags) > 0:
                self.log(f"✅ Found {len(script_tags)} script tags", "PASS")
                
                # Check if scripts are loaded in proper order
                if "defer" in html_content or "async" in html_content:
                    self.log("✅ Scripts use defer/async (good for extension compatibility)", "PASS")
                else:
                    self.log("⚠️ Scripts may load synchronously (could conflict with extensions)", "WARN")
            else:
                self.log("❌ No script tags found", "FAIL")
                return False
            
            # Check for proper event handling
            if "addEventListener" in html_content:
                self.log("✅ App uses addEventListener (good for extension compatibility)", "PASS")
            else:
                self.log("⚠️ App may not use proper event handling", "WARN")
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_undefined_variable_handling(self):
        """Test 4: Check for undefined variable issues"""
        self.log("=" * 60)
        self.log("TEST 4: Undefined Variable Handling Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            undefined_issues = []
            
            for script_path in script_urls[:2]:  # Check first 2 bundles
                script_url = f"{self.frontend_url}{script_path}"
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # Check for common undefined variable patterns
                    undefined_patterns = [
                        r"console\.log\(undefined\)",
                        r"console\.log\(.*undefined.*\)",
                        r"return undefined",
                        r"= undefined",
                        r"== undefined",
                        r"=== undefined"
                    ]
                    
                    for pattern in undefined_patterns:
                        matches = re.findall(pattern, script_content)
                        if matches:
                            undefined_issues.extend([f"{pattern} in {script_path}"] * len(matches))
                    
                    # Check for proper undefined handling
                    if "typeof" in script_content and "undefined" in script_content:
                        self.log(f"✅ {script_path} uses proper undefined checking", "PASS")
                    elif "undefined" in script_content:
                        self.log(f"⚠️ {script_path} references undefined but may not check properly", "WARN")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️ Could not check {script_path}: {e}", "WARN")
                    continue
            
            if undefined_issues:
                self.log(f"⚠️ Found undefined variable issues:", "WARN")
                for issue in undefined_issues[:5]:  # Show first 5
                    self.log(f"   {issue}", "WARN")
            else:
                self.log("✅ No undefined variable issues found", "PASS")
            
            return len(undefined_issues) == 0
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🚀 CONTENT SCRIPT AND BROWSER EXTENSION COMPATIBILITY TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # Test 1: Content script conflicts
        results.append(("Content Script Conflicts", self.test_no_content_script_conflicts()))
        
        # Test 2: Console output handling
        results.append(("Console Output Handling", self.test_console_output_handling()))
        
        # Test 3: Browser extension compatibility
        results.append(("Browser Extension Compatibility", self.test_browser_extension_compatibility()))
        
        # Test 4: Undefined variable handling
        results.append(("Undefined Variable Handling", self.test_undefined_variable_handling()))
        
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
    tester = ContentScriptCompatibilityTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

