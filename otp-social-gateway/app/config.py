"""Configuration management using environment variables"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Telegram Bot Configuration
    telegram_bot_token: str = ""
    
    # OTP Configuration
    default_expire_seconds: int = 30
    min_expire_seconds: int = 5
    max_expire_seconds: int = 60
    
    # Rate Limiting
    rate_limit_per_user: int = 5
    rate_limit_window_hours: int = 1
    
    # Server Configuration
    port: int = 55155
    host: str = "0.0.0.0"
    log_level: str = "INFO"
    
    # Custom message template
    message_template: str = "🔐 Your OTP is: {otp}\n\n⏱ Expires in {sec} seconds.\n\n⚠️ This message will self-destruct."
    
    # Magic Link Configuration
    magic_link_base_url: str = "http://localhost:5573"
    magic_link_secret: str = "your-magic-link-secret-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()