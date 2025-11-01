"""Telegram User Service - Simple MongoDB operations for user management"""
import logging
from typing import Optional, Dict
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class TelegramUserService:
    """Simple service for Telegram user operations - KISS approach"""
    
    def __init__(self, db):
        """Initialize with MongoDB database connection"""
        self.db = db
    
    async def get_user_by_telegram_id(self, telegram_user_id: int) -> Optional[Dict]:
        """Get registered user by Telegram User ID (or chat_id as fallback)"""
        # KISS: Query with $or for backwards compatibility - check both integer and string formats
        # Some users might have telegram_chat_id as number, others as string
        user = await self.db.users.find_one({
            "$or": [
                {"telegram_user_id": telegram_user_id},  # Integer match
                {"telegram_chat_id": str(telegram_user_id)},  # String match
                {"telegram_chat_id": telegram_user_id}  # Integer match (fallback for old data)
            ],
            "is_verified": True
        })
        if user:
            logger.info(f"✅ Found registered user: id={user.get('id')}, telegram_user_id={user.get('telegram_user_id')}, telegram_chat_id={user.get('telegram_chat_id')}")
        else:
            logger.warning(f"❌ No registered user found for telegram_user_id={telegram_user_id}")
            # Try one more fallback: check if telegram_chat_id matches as string in any format
            # This handles cases where telegram_chat_id might be stored differently
            fallback_user = await self.db.users.find_one({
                "$expr": {
                    "$or": [
                        {"$eq": ["$telegram_chat_id", str(telegram_user_id)]},
                        {"$eq": ["$telegram_chat_id", telegram_user_id]}
                    ]
                },
                "is_verified": True
            })
            if fallback_user:
                logger.info(f"✅ Found user via fallback query: id={fallback_user.get('id')}, telegram_chat_id={fallback_user.get('telegram_chat_id')}")
                user = fallback_user
        return user
    
    async def get_user_by_telegram_username(self, telegram_username: str) -> Optional[Dict]:
        """Get registered user by Telegram username (fallback method)"""
        if not telegram_username:
            return None
        user = await self.db.users.find_one({
            "telegram_username": telegram_username,
            "is_verified": True
        })
        if user:
            logger.info(f"✅ Found user by Telegram username: {telegram_username}")
        return user
    
    async def check_registration_status(self, telegram_user_id: int) -> Dict:
        """Check if user is registered and verified - KISS: Simple boolean check"""
        user = await self.get_user_by_telegram_id(telegram_user_id)
        
        if user:
            return {
                "is_registered": True,
                "is_verified": user.get("is_verified", False),
                "user": user
            }
        
        return {
            "is_registered": False,
            "is_verified": False,
            "user": None
        }
    
    async def save_telegram_profile(self, user_data: dict):
        """Save Telegram profile for unregistered user - KISS: Simple upsert"""
        if not user_data or "id" not in user_data:
            logger.warning("Invalid user_data provided to save_telegram_profile")
            return
        
        telegram_user_id = user_data.get("id")
        if not telegram_user_id:
            return
        
        # KISS: Simple upsert operation
        await self.db.telegram_users.update_one(
            {"telegram_user_id": telegram_user_id},
            {"$set": {
                "telegram_user_id": telegram_user_id,
                "telegram_username": user_data.get("username"),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name"),
                "language_code": user_data.get("language_code", "en"),
                "is_premium": user_data.get("is_premium", False),
                "collected_at": datetime.now(timezone.utc),
                "registration_pending": True
            }},
            upsert=True
        )
        logger.info(f"Saved Telegram profile for user {telegram_user_id}")
    
    async def check_name_availability(self, name: str) -> Dict:
        """Check if name is available - KISS: Simple case-insensitive check"""
        if not name or not name.strip():
            return {
                "available": False,
                "suggestion": None,
                "message": "Name cannot be empty"
            }
        
        # KISS: Case-insensitive regex search
        existing_user = await self.db.users.find_one({
            "name": {"$regex": f"^{name}$", "$options": "i"}
        })
        
        if existing_user:
            return {
                "available": False,
                "suggestion": None,
                "message": f"Name '{name}' is already taken. Please choose a different name."
            }
        
        return {
            "available": True,
            "suggestion": name,
            "message": None
        }

