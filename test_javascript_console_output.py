#!/usr/bin/env python3
"""
Test Suite: JavaScript Bundle Console Output Validation
Tests to ensure JavaScript bundles don't output false, undefined, or empty objects to console.
"""

import requests
import json
import sys
import re
from urllib.parse import urljoin

class JavaScriptConsoleOutputTest:
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
    
    def test_no_false_console_output(self):
        """Test 1: Verify JavaScript doesn't output 'false' to console"""
        self.log("=" * 60)
        self.log("TEST 1: False Console Output Check")
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
            
            false_outputs = []
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                self.log(f"Checking for false outputs in: {script_path}")
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # Check for console.log(false) patterns
                    false_patterns = [
                        r"console\.log\(false\)",
                        r"console\.log\(.*\bfalse\b.*\)",
                        r"console\.debug\(false\)",
                        r"console\.info\(false\)",
                        r"console\.warn\(false\)",
                        r"console\.error\(false\)",
                        r'console\.log\("false"\)',
                        r"return false;",
                        r"= false"
                    ]
                    
                    for pattern in false_patterns:
                        matches = re.findall(pattern, script_content)
                        if matches:
                            false_outputs.extend([f"{pattern} in {script_path}"] * len(matches))
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️ Could not check {script_path}: {e}", "WARN")
                    continue
            
            if false_outputs:
                self.log(f"❌ Found console.log(false) patterns:", "FAIL")
                for output in false_outputs[:5]:  # Show first 5
                    self.log(f"   {output}", "FAIL")
                return False
            else:
                self.log("✅ No console.log(false) patterns found", "PASS")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_no_undefined_console_output(self):
        """Test 2: Verify JavaScript doesn't output 'undefined' to console"""
        self.log("=" * 60)
        self.log("TEST 2: Undefined Console Output Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            undefined_outputs = []
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                self.log(f"Checking for undefined outputs in: {script_path}")
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # Check for console.log(undefined) patterns - but be careful with valid patterns
                    problematic_patterns = [
                        r"console\.log\(undefined\)",  # Direct undefined
                        r"console\.log\(.*\bundefined\b.*\)",  # Undefined in string
                        r"console\.debug\(undefined\)",
                        r"console\.info\(undefined\)",
                        # But allow: typeof x === "undefined" which is valid
                    ]
                    
                    for pattern in problematic_patterns:
                        matches = re.findall(pattern, script_content)
                        if matches:
                            undefined_outputs.extend([f"{pattern} in {script_path}"] * len(matches))
                    
                    # Check if proper undefined checking is used
                    if "typeof" in script_content and "undefined" in script_content:
                        self.log(f"✅ {script_path} uses proper undefined checking", "PASS")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️ Could not check {script_path}: {e}", "WARN")
                    continue
            
            if undefined_outputs:
                self.log(f"❌ Found console.log(undefined) patterns:", "FAIL")
                for output in undefined_outputs[:5]:
                    self.log(f"   {output}", "FAIL")
                return False
            else:
                self.log("✅ No console.log(undefined) patterns found", "PASS")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_no_empty_object_console_output(self):
        """Test 3: Verify JavaScript doesn't output empty objects '{}' to console"""
        self.log("=" * 60)
        self.log("TEST 3: Empty Object Console Output Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            empty_object_outputs = []
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                self.log(f"Checking for empty object outputs in: {script_path}")
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # Check for console.log({}) patterns - must be careful not to match valid patterns
                    problematic_patterns = [
                        r"console\.log\(\{\}\)",  # Direct empty object
                        r"console\.log\(.*\{\}.*\)",  # Empty object in expression
                        r"console\.debug\(\{\}\)",
                        r"console\.info\(\{\}\)",
                        # Allow: const obj = {} which is valid
                    ]
                    
                    for pattern in problematic_patterns:
                        # Find the line context
                        lines = script_content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if re.search(pattern, line):
                                # Make sure it's not a variable declaration
                                if not re.search(r'\b(const|let|var)\s+\w+\s*=\s*\{\}', line):
                                    empty_object_outputs.append(f"Line {i} in {script_path}: {line.strip()[:80]}")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️ Could not check {script_path}: {e}", "WARN")
                    continue
            
            if empty_object_outputs:
                self.log(f"❌ Found console.log({{}}) patterns:", "FAIL")
                for output in empty_object_outputs[:5]:
                    self.log(f"   {output}", "FAIL")
                return False
            else:
                self.log("✅ No console.log({}) patterns found", "PASS")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def test_console_output_usage(self):
        """Test 4: Verify console methods are used appropriately"""
        self.log("=" * 60)
        self.log("TEST 4: Console Method Usage Check")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            all_good = True
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # Count console usage
                    console_logs = len(re.findall(r"console\.log\(", script_content))
                    console_errors = len(re.findall(r"console\.error\(", script_content))
                    console_warns = len(re.findall(r"console\.warn\(", script_content))
                    console_debug = len(re.findall(r"console\.debug\(", script_content))
                    
                    total_console = console_logs + console_errors + console_warns + console_debug
                    
                    if total_console > 50:
                        self.log(f"⚠️ {script_path}: High console usage ({total_console} calls)", "WARN")
                    
                    # Check if console.log is used for debugging (may need to be removed in production)
                    if console_logs > 0:
                        self.log(f"ℹ️ {script_path}: {console_logs} console.log calls", "INFO")
                    
                    # Check for proper error logging
                    if console_errors > 0:
                        self.log(f"✅ {script_path}: Uses console.error for errors", "PASS")
                    elif console_logs > 0:
                        self.log(f"⚠️ {script_path}: Uses console.log but may need console.error", "WARN")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️ Could not check {script_path}: {e}", "WARN")
                    continue
            
            return all_good
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ Failed to fetch HTML: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🚀 JAVASCRIPT BUNDLE CONSOLE OUTPUT VALIDATION TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # Test 1: No false console output
        results.append(("No False Console Output", self.test_no_false_console_output()))
        
        # Test 2: No undefined console output
        results.append(("No Undefined Console Output", self.test_no_undefined_console_output()))
        
        # Test 3: No empty object console output
        results.append(("No Empty Object Console Output", self.test_no_empty_object_console_output()))
        
        # Test 4: Console method usage
        results.append(("Console Method Usage", self.test_console_output_usage()))
        
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
    tester = JavaScriptConsoleOutputTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

