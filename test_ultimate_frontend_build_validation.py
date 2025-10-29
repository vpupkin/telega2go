#!/usr/bin/env python3
"""
Test Suite: ULTIMATE PENALTY - Frontend Build and Deployment Validation
This test ensures the frontend is properly built and deployed with correct configuration.
"""

import requests
import json
import sys
import re
import subprocess
from urllib.parse import urljoin

class UltimateFrontendBuildValidationTest:
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
            "CRITICAL": "🚨",
            "PENALTY": "💀",
            "ULTIMATE": "🔥"
        }.get(level, "ℹ️")
        print(f"{prefix} {message}")
        self.test_results.append({"level": level, "message": message})
    
    def test_frontend_build_environment_variables(self):
        """ULTIMATE PENALTY TEST: Verify frontend build uses correct environment variables"""
        self.log("=" * 60)
        self.log("🔥 ULTIMATE PENALTY TEST: Frontend Build Environment Variables")
        self.log("=" * 60)
        
        try:
            # Check if we can access the Docker container
            result = subprocess.run(['docker', 'ps', '--filter', 'name=telega2go-frontend', '--format', '{{.Names}}'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0 or not result.stdout.strip():
                self.log("❌ ULTIMATE: Frontend container not running", "FAIL")
                return False
            
            container_name = result.stdout.strip()
            self.log(f"Found frontend container: {container_name}", "INFO")
            
            # Check environment variables in container
            env_result = subprocess.run(['docker', 'exec', container_name, 'env'], 
                                      capture_output=True, text=True, timeout=10)
            
            if env_result.returncode != 0:
                self.log("❌ ULTIMATE: Could not check container environment", "FAIL")
                return False
            
            env_output = env_result.stdout
            
            # Check for correct backend URL
            if f"REACT_APP_BACKEND_URL=https://putana.date:{self.new_port}" in env_output:
                self.log("✅ ULTIMATE: Correct backend URL environment variable", "PASS")
            elif f"REACT_APP_BACKEND_URL=http://localhost:{self.old_port}" in env_output:
                self.log("❌ ULTIMATE: OLD backend URL environment variable found!", "FAIL")
                return False
            elif f"REACT_APP_BACKEND_URL=https://putana.date:{self.old_port}" in env_output:
                self.log("❌ ULTIMATE: OLD backend URL with new domain found!", "FAIL")
                return False
            else:
                self.log("⚠️ ULTIMATE: Backend URL environment variable not found or different", "WARN")
            
            # Check for OTP Gateway URL
            if f"REACT_APP_OTP_GATEWAY_URL=https://putana.date:{self.new_port-1}" in env_output:
                self.log("✅ ULTIMATE: Correct OTP Gateway URL environment variable", "PASS")
            else:
                self.log("⚠️ ULTIMATE: OTP Gateway URL environment variable may be incorrect", "WARN")
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log("❌ ULTIMATE: Docker command timed out", "FAIL")
            return False
        except Exception as e:
            self.log(f"❌ ULTIMATE: Failed to check environment variables: {e}", "FAIL")
            return False
    
    def test_frontend_build_output_validation(self):
        """ULTIMATE PENALTY TEST: Validate frontend build output"""
        self.log("=" * 60)
        self.log("🔥 ULTIMATE PENALTY TEST: Frontend Build Output Validation")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Check for build artifacts
            build_artifacts = [
                r'<script[^>]*src=["\']/static/js/[^"\']+\.js["\'][^>]*>',
                r'<link[^>]*href=["\']/static/css/[^"\']+\.css["\'][^>]*>',
                r'<link[^>]*rel=["\']manifest["\'][^>]*>',
                r'<link[^>]*rel=["\']apple-touch-icon["\'][^>]*>'
            ]
            
            found_artifacts = []
            for pattern in build_artifacts:
                if re.search(pattern, html_content):
                    found_artifacts.append(pattern)
            
            if len(found_artifacts) >= 3:
                self.log("✅ ULTIMATE: Frontend build artifacts found", "PASS")
            else:
                self.log(f"❌ ULTIMATE: Missing build artifacts (found {len(found_artifacts)}/4)", "FAIL")
                return False
            
            # Check for React app structure
            react_patterns = [
                r'<div[^>]*id=["\']root["\'][^>]*>',
                r'<noscript[^>]*>You need to enable JavaScript',
                r'serviceWorker.*register'
            ]
            
            react_found = []
            for pattern in react_patterns:
                if re.search(pattern, html_content):
                    react_found.append(pattern)
            
            if len(react_found) >= 2:
                self.log("✅ ULTIMATE: React app structure found", "PASS")
            else:
                self.log(f"❌ ULTIMATE: Missing React app structure (found {len(react_found)}/3)", "FAIL")
                return False
            
            return True
            
        except requests.exceptions.RequestException as e:
            self.log(f"❌ ULTIMATE: Failed to validate build output: {e}", "FAIL")
            return False
    
    def test_frontend_runtime_configuration(self):
        """ULTIMATE PENALTY TEST: Verify frontend runtime configuration"""
        self.log("=" * 60)
        self.log("🔥 ULTIMATE PENALTY TEST: Frontend Runtime Configuration")
        self.log("=" * 60)
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract JavaScript bundle URLs
            script_urls = re.findall(r'<script[^>]*src=["\'](/static/js/[^"\']+\.js)["\'][^>]*>', html_content)
            
            if not script_urls:
                self.log("❌ ULTIMATE: No JavaScript bundles found", "FAIL")
                return False
            
            runtime_errors = []
            
            for script_path in script_urls:
                script_url = f"{self.frontend_url}{script_path}"
                
                try:
                    script_response = requests.get(script_url, timeout=10)
                    script_response.raise_for_status()
                    script_content = script_response.text
                    
                    # Check for runtime configuration patterns
                    config_patterns = [
                        # Correct patterns (should be present)
                        f"putana.date:{self.new_port}",
                        f"https://putana.date:{self.new_port}",
                        f"REACT_APP_BACKEND_URL",
                        
                        # Incorrect patterns (should NOT be present)
                        f"localhost:{self.old_port}",
                        f"127.0.0.1:{self.old_port}",
                        f"putana.date:{self.old_port}",
                        f"https://putana.date:{self.old_port}",
                        f"http://localhost:{self.old_port}",
                        f"http://127.0.0.1:{self.old_port}"
                    ]
                    
                    correct_found = False
                    incorrect_found = False
                    
                    for pattern in config_patterns[:3]:  # Check correct patterns
                        if pattern in script_content:
                            correct_found = True
                            self.log(f"✅ ULTIMATE: Found correct config pattern: {pattern}", "PASS")
                    
                    for pattern in config_patterns[3:]:  # Check incorrect patterns
                        if pattern in script_content:
                            incorrect_found = True
                            runtime_errors.append(f"🔥 ULTIMATE ERROR: Found incorrect config pattern: {pattern}")
                    
                    if incorrect_found:
                        self.log(f"❌ ULTIMATE: Found incorrect configuration in {script_path}", "FAIL")
                    
                except requests.exceptions.RequestException as e:
                    self.log(f"⚠️ ULTIMATE: Could not check {script_path}: {e}", "WARN")
                    continue
            
            if runtime_errors:
                self.log(f"🔥 ULTIMATE PENALTY: Found {len(runtime_errors)} runtime configuration errors!", "ULTIMATE")
                for error in runtime_errors[:10]:
                    self.log(error, "ULTIMATE")
                return False
            else:
                self.log("✅ ULTIMATE: No runtime configuration errors found", "PASS")
                return True
                
        except requests.exceptions.RequestException as e:
            self.log(f"❌ ULTIMATE: Failed to check runtime configuration: {e}", "FAIL")
            return False
    
    def test_frontend_docker_container_health(self):
        """ULTIMATE PENALTY TEST: Verify frontend Docker container health"""
        self.log("=" * 60)
        self.log("🔥 ULTIMATE PENALTY TEST: Frontend Docker Container Health")
        self.log("=" * 60)
        
        try:
            # Check container status
            result = subprocess.run(['docker', 'ps', '--filter', 'name=telega2go-frontend', '--format', 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                self.log("❌ ULTIMATE: Could not check container status", "FAIL")
                return False
            
            output = result.stdout.strip()
            if not output or "telega2go-frontend" not in output:
                self.log("❌ ULTIMATE: Frontend container not found", "FAIL")
                return False
            
            self.log(f"Container status: {output}", "INFO")
            
            # Check if container is healthy
            if "healthy" in output.lower():
                self.log("✅ ULTIMATE: Container is healthy", "PASS")
            elif "unhealthy" in output.lower():
                self.log("❌ ULTIMATE: Container is unhealthy", "FAIL")
                return False
            else:
                self.log("⚠️ ULTIMATE: Container health status unknown", "WARN")
            
            # Check port mapping
            if f"55553->80" in output:
                self.log("✅ ULTIMATE: Correct port mapping (55553->80)", "PASS")
            else:
                self.log("❌ ULTIMATE: Incorrect port mapping", "FAIL")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log("❌ ULTIMATE: Docker command timed out", "FAIL")
            return False
        except Exception as e:
            self.log(f"❌ ULTIMATE: Failed to check container health: {e}", "FAIL")
            return False
    
    def test_frontend_nginx_configuration(self):
        """ULTIMATE PENALTY TEST: Verify frontend nginx configuration"""
        self.log("=" * 60)
        self.log("🔥 ULTIMATE PENALTY TEST: Frontend Nginx Configuration")
        self.log("=" * 60)
        
        try:
            # Check if we can access nginx config in container
            result = subprocess.run(['docker', 'exec', 'telega2go-frontend', 'cat', '/etc/nginx/conf.d/default.conf'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                self.log("⚠️ ULTIMATE: Could not access nginx config (may not be nginx-based)", "WARN")
                return True  # Not a failure if not using nginx
            
            nginx_config = result.stdout
            
            # Check for proper nginx configuration
            nginx_patterns = [
                r"listen\s+80",
                r"root\s+/usr/share/nginx/html",
                r"index\s+index\.html",
                r"try_files.*index\.html"
            ]
            
            found_patterns = []
            for pattern in nginx_patterns:
                if re.search(pattern, nginx_config):
                    found_patterns.append(pattern)
            
            if len(found_patterns) >= 3:
                self.log("✅ ULTIMATE: Nginx configuration looks correct", "PASS")
            else:
                self.log(f"⚠️ ULTIMATE: Nginx configuration may be incomplete (found {len(found_patterns)}/4 patterns)", "WARN")
            
            return True
            
        except subprocess.TimeoutExpired:
            self.log("❌ ULTIMATE: Docker command timed out", "FAIL")
            return False
        except Exception as e:
            self.log(f"❌ ULTIMATE: Failed to check nginx configuration: {e}", "FAIL")
            return False
    
    def run_all_tests(self):
        """Run all ULTIMATE PENALTY tests"""
        print("\n" + "=" * 60)
        print("🔥 ULTIMATE PENALTY - FRONTEND BUILD AND DEPLOYMENT VALIDATION TEST SUITE")
        print("=" * 60 + "\n")
        
        results = []
        
        # ULTIMATE PENALTY Test 1: Environment variables
        results.append(("ULTIMATE PENALTY: Environment Variables", self.test_frontend_build_environment_variables()))
        
        # ULTIMATE PENALTY Test 2: Build output validation
        results.append(("ULTIMATE PENALTY: Build Output Validation", self.test_frontend_build_output_validation()))
        
        # ULTIMATE PENALTY Test 3: Runtime configuration
        results.append(("ULTIMATE PENALTY: Runtime Configuration", self.test_frontend_runtime_configuration()))
        
        # ULTIMATE PENALTY Test 4: Container health
        results.append(("ULTIMATE PENALTY: Container Health", self.test_frontend_docker_container_health()))
        
        # ULTIMATE PENALTY Test 5: Nginx configuration
        results.append(("ULTIMATE PENALTY: Nginx Configuration", self.test_frontend_nginx_configuration()))
        
        # Summary
        print("\n" + "=" * 60)
        print("🔥 ULTIMATE PENALTY TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "🔥 ULTIMATE PENALTY FAIL"
            print(f"{status}: {test_name}")
        
        print("\n" + "=" * 60)
        print(f"🔥 ULTIMATE PENALTY Results: {passed}/{total} tests passed")
        if passed < total:
            print("🔥 ULTIMATE PENALTY: CRITICAL BUILD/DEPLOYMENT ISSUES FOUND!")
            print("🔥 PENALTY LEVEL: ULTIMATE - FRONTEND BUILD/DEPLOYMENT MUST BE FIXED!")
        print("=" * 60 + "\n")
        
        return passed == total

if __name__ == "__main__":
    tester = UltimateFrontendBuildValidationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

