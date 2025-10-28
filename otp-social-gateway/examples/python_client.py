#!/usr/bin/env python3
"""Example Python client for OTP Social Gateway"""

import requests
import random
import sys
from typing import Optional


class OTPGatewayClient:
    """Client for OTP Social Gateway API"""
    
    def __init__(self, base_url: str = "http://localhost:55155"):
        self.base_url = base_url.rstrip('/')
    
    def send_otp(
        self, 
        chat_id: str, 
        otp: str, 
        expire_seconds: Optional[int] = 30
    ) -> dict:
        """
        Send OTP to Telegram user
        
        Args:
            chat_id: Telegram user chat ID
            otp: One-Time Password (4-8 digits)
            expire_seconds: Auto-delete after seconds (5-60)
            
        Returns:
            Response dictionary
        """
        url = f"{self.base_url}/send-otp"
        payload = {
            "chat_id": chat_id,
            "otp": otp,
            "expire_seconds": expire_seconds
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
    
    def health_check(self) -> dict:
        """Check if service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics"""
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=5)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error: {e}"
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate random OTP"""
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def main():
    """Example usage"""
    # Initialize client
    client = OTPGatewayClient("http://localhost:55155")
    
    # Check health
    print("Checking service health...")
    health = client.health_check()
    print(f"Health: {health}\n")
    
    if health.get('status') != 'ok':
        print("❌ Service is not healthy!")
        sys.exit(1)
    
    # Get chat ID from command line or use default
    chat_id = sys.argv[1] if len(sys.argv) > 1 else "123456789"
    
    # Generate and send OTP
    otp = client.generate_otp(6)
    print(f"Sending OTP {otp} to chat_id {chat_id}...")
    
    result = client.send_otp(
        chat_id=chat_id,
        otp=otp,
        expire_seconds=30
    )
    
    if result.get('success'):
        print("✅ OTP sent successfully!")
        print(f"   Message ID: {result['message_id']}")
        print(f"   Sent at: {result['sent_at']}")
        print(f"   Will delete at: {result['delete_at']}")
    else:
        print(f"❌ Failed to send OTP: {result.get('error')}")
        if 'details' in result:
            print(f"   Details: {result['details']}")
    
    # Show metrics
    print("\n" + "="*60)
    print("Metrics:")
    print("="*60)
    metrics = client.get_metrics()
    for line in metrics.split('\n'):
        if line.startswith('otp_') or line.startswith('rate_limit_'):
            print(line)


if __name__ == "__main__":
    main()