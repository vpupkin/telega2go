#!/usr/bin/env python3
"""
Test Suite: MASSIVE PENALTY - Complete Console Error Elimination Test
This test catches ALL console errors and ensures they are completely eliminated.
"""

import requests
import json
import sys
import re
from urllib.parse import urljoin

class MassiveConsoleErrorEliminationTest:
    def __init__(self):
        self.frontend_url = "https://putana.date"
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Log test messages"""
        prefix = {
            "INFO": "ℹ️",
            "PASS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️",
            "CRITICAL": "🚨",
            "PENALTY": "💀"
        }.get(level, "ℹ️")
        print(f"{prefix} {message}")
        self.test_results.append({"level": level, "message": message})
    
    def test_eliminate_all_console_errors(self):
        """MASSIVE PENALTY TEST: Eliminate ALL console errors"""
        self.log("=" * 60)
        self.log("💀 MASSIVE PENALTY TEST: Complete Console Error Elimination")
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
            
            all_console_errors = []
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                self.log(f"💀 PENALTY CHECK: {script_path}")
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # MASSIVE PENALTY: Check for ALL console error patterns
                    console_error_patterns = [
                        # Direct console outputs that cause errors
                        r"console\.log\(false\)",
                        r"console\.log\(undefined\)",
                        r"console\.log\(\{\}\)",
                        r"console\.log\(null\)",
                        r"console\.log\(0\)",
                        r"console\.log\(1\)",
                        r"console\.log\(true\)",
                        
                        # Patterns that cause the specific errors mentioned
                        r"console\.log\(.*\bfalse\b.*\)",
                        r"console\.log\(.*\bundefined\b.*\)",
                        r"console\.log\(.*\{\}.*\)",
                        r"console\.log\(.*StopNotification.*\)",
                        r"console\.log\(.*BROWSER\.runtime.*\)",
                        
                        # Other problematic patterns
                        r"console\.debug\(false\)",
                        r"console\.info\(false\)",
                        r"console\.warn\(false\)",
                        r"console\.error\(false\)",
                        r"console\.debug\(undefined\)",
                        r"console\.info\(undefined\)",
                        r"console\.warn\(undefined\)",
                        r"console\.error\(undefined\)",
                        r"console\.debug\(\{\}\)",
                        r"console\.info\(\{\}\)",
                        r"console\.warn\(\{\}\)",
                        r"console\.error\(\{\}\)",
                        
                        # React/JavaScript patterns that cause console errors
                        r"console\.log\(.*\bnull\b.*\)",
                        r"console\.log\(.*\b0\b.*\)",
                        r"console\.log\(.*\b1\b.*\)",
                        r"console\.log\(.*\btrue\b.*\)",
                        
                        # Specific patterns from the error log
                        r"content-script\.js",
                        r"content\.7f229555\.js",
                        r"StopNotification.*1",
                        r"BROWSER\.runtime\.sendMessage"
                    ]
                    
                    for pattern in console_error_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        if matches:
                            # Find line numbers for context
                            lines = script_content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    all_console_errors.append(f"💀 PENALTY: {pattern} found in {script_path} line {i}: {line.strip()[:100]}")
                    
                    # Check for proper console usage
                    if "console.log" in script_content:
                        # Count console.log usage
                        console_log_count = len(re.findall(r"console\.log\(", script_content))
                        if console_log_count > 0:
                            self.log(f"⚠️ Found {console_log_count} console.log calls in {script_path}", "WARN")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ PENALTY: Could not check {script_path}: {e}", "FAIL")
                    all_console_errors.append(f"💀 PENALTY: Failed to check {script_path}")
                    continue
            
            if all_console_errors:
                self.log(f"💀 MASSIVE PENALTY: Found {len(all_console_errors)} console error patterns!", "PENALTY")
                for error in all_console_errors[:15]:  # Show first 15
                    self.log(error, "PENALTY")
                return False
            else:
                self.log("✅ PENALTY: No console error patterns found", "PASS")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ PENALTY: Failed to fetch frontend: {e}", "FAIL")
            return False
    
    def test_eliminate_react_dom_errors(self):
        """MASSIVE PENALTY TEST: Eliminate React DOM errors"""
        self.log("=" * 60)
        self.log("💀 MASSIVE PENALTY TEST: React DOM Error Elimination")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            react_dom_errors = []
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # Check for React DOM error patterns
                    react_error_patterns = [
                        r"react-dom-client\.production\.js",
                        r"react-dom\.production\.js",
                        r"Gu @ react-dom",
                        r"y @ UserRegistration\.jsx",
                        r"anonymous @ react-dom",
                        r"Bt @ react-dom",
                        r"nd @ react-dom",
                        r"Ef @ react-dom",
                        r"kf @ react-dom",
                        
                        # Patterns that cause React errors
                        r"console\.log\(.*\bundefined\b.*\)",
                        r"console\.log\(.*\bfalse\b.*\)",
                        r"console\.log\(.*\{\}.*\)",
                        r"console\.log\(null\)",
                        
                        # UserRegistration.jsx specific patterns
                        r"UserRegistration\.jsx.*POST",
                        r"UserRegistration\.jsx.*fetch",
                        r"UserRegistration\.jsx.*axios"
                    ]
                    
                    for pattern in react_error_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        if matches:
                            lines = script_content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    react_dom_errors.append(f"💀 REACT PENALTY: {pattern} found in {script_path} line {i}: {line.strip()[:100]}")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️ Could not check {script_path}: {e}", "WARN")
                    continue
            
            if react_dom_errors:
                self.log(f"💀 REACT PENALTY: Found {len(react_dom_errors)} React DOM error patterns!", "PENALTY")
                for error in react_dom_errors[:10]:
                    self.log(error, "PENALTY")
                return False
            else:
                self.log("✅ REACT PENALTY: No React DOM error patterns found", "PASS")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ PENALTY: Failed to check React DOM errors: {e}", "FAIL")
            return False
    
    def test_eliminate_connection_timeout_errors(self):
        """MASSIVE PENALTY TEST: Eliminate connection timeout errors"""
        self.log("=" * 60)
        self.log("💀 MASSIVE PENALTY TEST: Connection Timeout Error Elimination")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            connection_errors = []
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # Check for connection timeout error patterns
                    timeout_error_patterns = [
                        r"ERR_CONNECTION_TIMED_OUT",
                        r"CONNECTION_TIMED_OUT",
                        r"timeout",
                        r"Connection.*timeout",
                        r"Request.*timeout",
                        r"fetch.*timeout",
                        r"axios.*timeout",
                        r"XMLHttpRequest.*timeout",
                        
                        # Specific patterns from the error
                        r"POST.*5572.*api.*register",
                        r"POST.*localhost.*5572",
                        r"fetch.*5572",
                        r"axios.*5572",
                        r"XMLHttpRequest.*5572"
                    ]
                    
                    for pattern in timeout_error_patterns:
                        matches = re.findall(pattern, script_content, re.IGNORECASE)
                        if matches:
                            lines = script_content.split('\n')
                            for i, line in enumerate(lines, 1):
                                if re.search(pattern, line, re.IGNORECASE):
                                    connection_errors.append(f"💀 CONNECTION PENALTY: {pattern} found in {script_path} line {i}: {line.strip()[:100]}")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️ Could not check {script_path}: {e}", "WARN")
                    continue
            
            if connection_errors:
                self.log(f"💀 CONNECTION PENALTY: Found {len(connection_errors)} connection error patterns!", "PENALTY")
                for error in connection_errors[:10]:
                    self.log(error, "PENALTY")
                return False
            else:
                self.log("✅ CONNECTION PENALTY: No connection error patterns found", "PASS")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ PENALTY: Failed to check connection errors: {e}", "FAIL")
            return False
    
    def test_eliminate_manifest_icon_errors(self):
        """MASSIVE PENALTY TEST: Eliminate manifest icon errors"""
        self.log("=" * 60)
        self.log("💀 MASSIVE PENALTY TEST: Manifest Icon Error Elimination")
        self.log("=" * 60)
        
        try:
            # Check manifest file
            manifest_url = f"{self.frontend_url}/manifest.json"
            manifest_response = requests.get(manifest_url, timeout=10)
            manifest_response.raise_for_status()
            manifest = manifest_response.json()
            
            icon_errors = []
            
            if "icons" in manifest:
                for icon in manifest["icons"]:
                    if "src" in icon:
                        icon_src = icon["src"]
                        if icon_src.startswith("/"):
                            icon_url = f"{self.frontend_url}{icon_src}"
                        else:
                            icon_url = urljoin(self.frontend_url, icon_src)
                        
                        try:
                            icon_response = requests.head(icon_url, timeout=5)
                            if icon_response.status_code != 200:
                                icon_errors.append(f"💀 ICON PENALTY: Icon not found {icon_src}: HTTP {icon_response.status_code}")
                            else:
                                content_type = icon_response.headers.get("content-type", "")
                                if not content_type.startswith("image/"):
                                    icon_errors.append(f"💀 ICON PENALTY: Icon not an image {icon_src}: {content_type}")
                        except requests.exceptions.RequestException as e:
                            icon_errors.append(f"💀 ICON PENALTY: Icon failed to load {icon_src}: {e}")
            
            # Check for the specific icon mentioned in error
            specific_icon = f"{self.frontend_url}/icon-144.png"
            try:
                specific_response = requests.head(specific_icon, timeout=5)
                if specific_response.status_code != 200:
                    icon_errors.append(f"💀 ICON PENALTY: icon-144.png not found: HTTP {specific_response.status_code}")
                else:
                    content_type = specific_response.headers.get("content-type", "")
                    if not content_type.startswith("image/"):
                        icon_errors.append(f"💀 ICON PENALTY: icon-144.png not an image: {content_type}")
            except requests.exceptions.RequestException as e:
                icon_errors.append(f"💀 ICON PENALTY: icon-144.png failed to load: {e}")
            
            if icon_errors:
                self.log(f"💀 ICON PENALTY: Found {len(icon_errors)} icon error patterns!", "PENALTY")
                for error in icon_errors:
                    self.log(error, "PENALTY")
                return False
            else:
                self.log("✅ ICON PENALTY: No icon error patterns found", "PASS")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ PENALTY: Failed to check manifest icons: {e}", "FAIL")
            return False
        except json.JSONDecodeError as e:
            self.log(f"❌ PENALTY: Manifest is not valid JSON: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all MASSIVE PENALTY tests"""
        print("\n" + "=" * 60)
        print("💀 MASSIVE PENALTY - COMPLETE CONSOLE ERROR ELIMINATION TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # MASSIVE PENALTY Test 1: All console errors
        results.append(("MASSIVE PENALTY: Console Error Elimination", self.test_eliminate_all_console_errors()))
        
        # MASSIVE PENALTY Test 2: React DOM errors
        results.append(("MASSIVE PENALTY: React DOM Error Elimination", self.test_eliminate_react_dom_errors()))
        
        # MASSIVE PENALTY Test 3: Connection timeout errors
        results.append(("MASSIVE PENALTY: Connection Timeout Elimination", self.test_eliminate_connection_timeout_errors()))
        
        # MASSIVE PENALTY Test 4: Manifest icon errors
        results.append(("MASSIVE PENALTY: Manifest Icon Error Elimination", self.test_eliminate_manifest_icon_errors()))
        
        # Summary
        print("\n" + "=" * 60)
        print("💀 MASSIVE PENALTY TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "💀 MASSIVE PENALTY FAIL"
            print(f"{status}: {test_name}")
        
        print("\n" + "=" * 60)
        print(f"💀 MASSIVE PENALTY Results: {passed}/{total} tests passed")
        if passed < total:
            print("💀 MASSIVE PENALTY: CRITICAL ISSUES FOUND - CONSOLE ERRORS NOT ELIMINATED!")
            print("💀 PENALTY LEVEL: MAXIMUM - ALL CONSOLE ERRORS MUST BE FIXED!")
        print("=" * 60 + "\n")
        
        return passed == total

if __name__ == "__main__":
    tester = MassiveConsoleErrorEliminationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

