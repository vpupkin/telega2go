#!/usr/bin/env python3
"""
🚀 Telega2Go Complete Test Runner
=================================

This is the ULTIMATE test runner that eliminates ALL manual testing.
It runs all test suites in sequence and provides comprehensive reporting.

Usage:
    python3 test_all.py

This script will:
1. Run basic functionality tests
2. Run advanced features tests  
3. Run complete automation tests
4. Generate comprehensive reports
5. Exit with proper status codes

NO MANUAL TESTING REQUIRED!
"""

import subprocess
import sys
import time
from datetime import datetime

def log(message, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"ℹ️  [{timestamp}] {message}")

def log_success(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"✅ [{timestamp}] {message}")

def log_error(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"❌ [{timestamp}] {message}")

def run_test(test_name, test_file):
    """Run a test file and return success status"""
    log(f"🧪 Running {test_name}...")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log_success(f"✅ {test_name} PASSED")
            return True
        else:
            log_error(f"❌ {test_name} FAILED")
            log_error(f"Error output: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log_error(f"❌ {test_name} TIMEOUT")
        return False
    except Exception as e:
        log_error(f"❌ {test_name} ERROR: {e}")
        return False

def main():
    """Run all test suites"""
    log("🚀 Starting Complete Test Suite")
    log("=" * 50)
    
    start_time = time.time()
    
    # Define test suites
    test_suites = [
        ("Basic Functionality", "test_basic_functionality.py"),
        ("Advanced Features", "test_advanced_features.py"),
        ("Complete Automation", "test_complete_automation.py")
    ]
    
    passed = 0
    total = len(test_suites)
    
    for test_name, test_file in test_suites:
        if run_test(test_name, test_file):
            passed += 1
        else:
            log_error(f"❌ {test_name} failed - stopping test suite")
            break
    
    duration = time.time() - start_time
    
    # Final summary
    log("\n" + "=" * 50)
    log(f"📊 Test Results: {passed}/{total} test suites passed")
    log(f"⏱️  Total Duration: {duration:.2f} seconds")
    
    if passed == total:
        log_success("🎉 ALL TEST SUITES PASSED! System is fully functional!")
        log_success("🚀 NO MANUAL TESTING REQUIRED!")
        exit(0)
    else:
        log_error(f"❌ {total - passed} test suites failed!")
        exit(1)

if __name__ == "__main__":
    main()
