"""Simple HTTP-based OTP service to avoid python-telegram-bot timeout issues"""
import asyncio
import httpx
import json
import qrcode
import io
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
from app.config import Settings

settings = Settings()

class SimpleOTPService:
    """Simple HTTP-based OTP service using direct Telegram API calls"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self._delivery_stats = {
            "total_sent": 0,
            "total_failed": 0,
            "total_deleted": 0
        }
    
    async def send_otp(
        self, 
        chat_id: str, 
        otp: str, 
        expire_seconds: int = 30,
        email: str = None
    ) -> Dict:
        """Send OTP via Telegram using direct HTTP calls"""
        try:
            # Generate magic link if email is provided
            magic_link = ""
            if email:
                magic_link = self._generate_magic_link(email, otp)
            
            if magic_link:
                # Send QR code with OTP info
                qr_code_bytes = self._generate_qr_code(magic_link)
                
                # Prepare photo data
                photo_data = {
                    'chat_id': chat_id,
                    'caption': (
                        f"🔐 Your OTP is: <b>{otp}</b>\n\n"
                        f"⏱ Expires in {expire_seconds} seconds.\n\n"
                        f"📱 Scan this QR code with your phone camera for instant verification!\n\n"
                        f"💡 Or tap the button below to verify instantly!\n\n"
                        f"⚠️ This message will self-destruct."
                    ),
                    'parse_mode': 'HTML'
                }
                
                # Create inline keyboard
                keyboard = [[{"text": "🔗 Click here to verify", "url": magic_link}]]
                photo_data['reply_markup'] = json.dumps({"inline_keyboard": keyboard})
                
                # Send photo with timeout
                async with httpx.AsyncClient(timeout=60.0) as client:
                    files = {'photo': ('qr_code.png', qr_code_bytes, 'image/png')}
                    response = await client.post(
                        f"{self.base_url}/sendPhoto",
                        data=photo_data,
                        files=files
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        message_id = result['result']['message_id']
                    else:
                        raise Exception(f"Telegram API error: {response.status_code} - {response.text}")
            else:
                # Send regular text message
                message_text = f"🔐 Your OTP is: <b>{otp}</b>\n\n⏱ Expires in {expire_seconds} seconds.\n\n⚠️ This message will self-destruct."
                
                message_data = {
                    'chat_id': chat_id,
                    'text': message_text,
                    'parse_mode': 'HTML'
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        f"{self.base_url}/sendMessage",
                        data=message_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        message_id = result['result']['message_id']
                    else:
                        raise Exception(f"Telegram API error: {response.status_code} - {response.text}")
            
            sent_at = datetime.now(timezone.utc)
            delete_at = sent_at + timedelta(seconds=expire_seconds)
            
            # Schedule auto-delete as background task
            if message_id:
                asyncio.create_task(self._auto_delete_message(chat_id, message_id, delete_at))
            
            # Update stats
            self._delivery_stats["total_sent"] += 1
            
            return {
                "success": True,
                "message_id": message_id,
                "sent_at": sent_at.isoformat(),
                "delete_at": delete_at.isoformat(),
                "chat_id": chat_id
            }
            
        except Exception as e:
            print(f"Failed to send OTP: {str(e)}")
            self._delivery_stats["total_failed"] += 1
            
            return {
                "success": False,
                "error": "Internal server error",
                "details": str(e)
            }
    
    def _generate_qr_code(self, data: str) -> bytes:
        """Generate QR code as bytes"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
    def _generate_magic_link(self, email: str, otp: str) -> str:
        """Generate magic link URL"""
        import time
        import hmac
        import hashlib
        import base64
        
        # Create token data
        token_time = str(int(time.time()))
        token_data = f"{email}:{otp}:{token_time}"
        
        # Create signature
        signature = hmac.new(
            settings.magic_link_secret.encode(),
            token_data.encode(),
            hashlib.sha256
        ).digest()
        
        # Combine data and signature
        full_token = f"{token_data}:{base64.urlsafe_b64encode(signature).decode()}"
        
        # Encode to base64 URL-safe
        token = base64.urlsafe_b64encode(full_token.encode()).decode()
        
        return f"{settings.magic_link_base_url}/verify-magic-link?token={token}"
    
    async def _auto_delete_message(self, chat_id: str, message_id: int, delete_at: datetime):
        """Auto-delete message after specified time"""
        try:
            # Calculate delay
            now = datetime.now(timezone.utc)
            delay_seconds = (delete_at - now).total_seconds()
            
            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)
            
            # Delete the message
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/deleteMessage",
                    data={
                        'chat_id': chat_id,
                        'message_id': message_id
                    }
                )
                
                if response.status_code == 200:
                    self._delivery_stats["total_deleted"] += 1
                else:
                    print(f"Failed to delete message: {response.status_code} - {response.text}")
                    
        except Exception as e:
            print(f"Error deleting message: {str(e)}")
    
    def get_stats(self) -> Dict:
        """Get delivery statistics"""
        return self._delivery_stats.copy()
