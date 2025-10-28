"""OTP delivery service using Telegram Bot API with auto-delete"""
import asyncio
import logging
import hmac
import hashlib
import base64
from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple
from telegram import Bot
from telegram.error import TelegramError, RetryAfter, TimedOut
from app.config import settings

logger = logging.getLogger(__name__)


class OTPService:
    """Service for sending OTPs via Telegram with self-destruct functionality"""
    
    def __init__(self, bot_token: str):
        """Initialize the OTP service with Telegram bot"""
        self.bot = Bot(token=bot_token)
        self._delivery_stats = {
            "total_sent": 0,
            "total_failed": 0,
            "total_deleted": 0
        }
    
    def _generate_magic_link(self, email: str, otp: str) -> str:
        """Generate a secure magic link for OTP verification"""
        # Create a token with email and OTP
        token_data = f"{email}:{otp}:{datetime.now(timezone.utc).timestamp()}"
        
        # Create HMAC signature
        signature = hmac.new(
            settings.magic_link_secret.encode(),
            token_data.encode(),
            hashlib.sha256
        ).digest()
        
        # Encode the token
        token = base64.urlsafe_b64encode(
            f"{token_data}:{base64.urlsafe_b64encode(signature).decode()}".encode()
        ).decode()
        
        # Return the magic link
        return f"{settings.magic_link_base_url}/verify?token={token}"
    
    async def send_otp(
        self, 
        chat_id: str, 
        otp: str, 
        expire_seconds: int = 30,
        email: str = None
    ) -> Tuple[bool, Dict]:
        """
        Send OTP to Telegram user and schedule auto-delete
        
        Args:
            chat_id: Telegram user chat ID
            otp: The OTP code to send
            expire_seconds: Seconds before message auto-deletes
            
        Returns:
            Tuple of (success: bool, response_data: dict)
        """
        try:
            # Generate magic link if email is provided
            magic_link = ""
            if email:
                magic_link = self._generate_magic_link(email, otp)
            
            # Format message using template
            if magic_link:
                message_text = f"🔐 Your OTP is: {otp}\n\n⏱ Expires in {expire_seconds} seconds.\n\n🚀 Or click this link to verify instantly:\n{magic_link}\n\n⚠️ This message will self-destruct."
            else:
                message_text = settings.message_template.format(
                    otp=otp,
                    sec=expire_seconds
                )
            
            # Send message with retry logic
            message = await self._send_with_retry(chat_id, message_text)
            
            sent_at = datetime.now(timezone.utc)
            delete_at = sent_at + timedelta(seconds=expire_seconds)
            
            # Schedule auto-delete as background task
            asyncio.create_task(
                self._auto_delete_message(chat_id, message.message_id, expire_seconds)
            )
            
            self._delivery_stats["total_sent"] += 1
            
            logger.info(
                "OTP sent successfully",
                extra={
                    "chat_id": chat_id,
                    "message_id": message.message_id,
                    "expire_seconds": expire_seconds,
                    "sent_at": sent_at.isoformat()
                }
            )
            
            return True, {
                "success": True,
                "message_id": message.message_id,
                "sent_at": sent_at.isoformat(),
                "delete_at": delete_at.isoformat(),
                "chat_id": chat_id
            }
            
        except TelegramError as e:
            self._delivery_stats["total_failed"] += 1
            logger.error(
                f"Failed to send OTP: {str(e)}",
                extra={
                    "chat_id": chat_id,
                    "error_type": type(e).__name__
                }
            )
            return False, {
                "success": False,
                "error": "Failed to send OTP",
                "details": str(e)
            }
        except Exception as e:
            self._delivery_stats["total_failed"] += 1
            logger.error(
                f"Unexpected error sending OTP: {str(e)}",
                extra={
                    "chat_id": chat_id,
                    "error_type": type(e).__name__
                }
            )
            return False, {
                "success": False,
                "error": "Internal server error",
                "details": str(e)
            }
    
    async def _send_with_retry(
        self, 
        chat_id: str, 
        message_text: str, 
        max_retries: int = 1
    ):
        """Send message with retry logic for transient failures"""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await self.bot.send_message(
                    chat_id=int(chat_id),
                    text=message_text,
                    parse_mode="HTML"
                )
            except (TimedOut, RetryAfter) as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = e.retry_after if isinstance(e, RetryAfter) else 1
                    logger.warning(f"Transient error, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
            except TelegramError as e:
                # Don't retry for non-transient errors
                raise e
        
        raise last_error
    
    async def _auto_delete_message(
        self, 
        chat_id: str, 
        message_id: int, 
        delay_seconds: int
    ):
        """Auto-delete message after specified delay"""
        try:
            await asyncio.sleep(delay_seconds)
            await self.bot.delete_message(
                chat_id=int(chat_id),
                message_id=message_id
            )
            self._delivery_stats["total_deleted"] += 1
            logger.info(
                "Message auto-deleted",
                extra={
                    "chat_id": chat_id,
                    "message_id": message_id
                }
            )
        except TelegramError as e:
            logger.warning(
                f"Failed to delete message: {str(e)}",
                extra={
                    "chat_id": chat_id,
                    "message_id": message_id
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error deleting message: {str(e)}")
    
    async def verify_bot_token(self) -> bool:
        """Verify that the bot token is valid"""
        try:
            bot_info = await asyncio.wait_for(self.bot.get_me(), timeout=30.0)
            logger.info(f"Bot verified: @{bot_info.username} ({bot_info.first_name})")
            return True
        except asyncio.TimeoutError:
            logger.error("Bot token verification timed out")
            return False
        except TelegramError as e:
            logger.error(f"Invalid bot token: {str(e)}")
            return False
    
    def get_stats(self) -> Dict:
        """Get delivery statistics"""
        return self._delivery_stats.copy()