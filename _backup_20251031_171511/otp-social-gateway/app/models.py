"""Pydantic models for request/response validation"""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional


class SendOTPRequest(BaseModel):
    """Request model for sending OTP"""
    chat_id: str = Field(..., description="Telegram user chat ID (numeric string)")
    otp: str = Field(..., description="One-Time Password (4-8 digits)")
    expire_seconds: Optional[int] = Field(30, description="Auto-delete after seconds (5-60)")
    email: Optional[str] = Field(None, description="User email for magic link generation")
    
    @validator('chat_id')
    def validate_chat_id(cls, v):
        """Ensure chat_id is a numeric string"""
        if not v.lstrip('-').isdigit():
            raise ValueError('chat_id must be a numeric string (can start with -)')
        return v
    
    @validator('otp')
    def validate_otp(cls, v):
        """Ensure OTP is 4-8 digits"""
        if not v.isdigit():
            raise ValueError('otp must contain only digits')
        if len(v) < 4 or len(v) > 8:
            raise ValueError('otp must be 4-8 digits long')
        return v
    
    @validator('expire_seconds')
    def validate_expire_seconds(cls, v):
        """Ensure expire_seconds is within allowed range"""
        if v is None:
            return 30
        if v < 5 or v > 60:
            raise ValueError('expire_seconds must be between 5 and 60')
        return v


class SendOTPResponse(BaseModel):
    """Response model for send OTP endpoint"""
    success: bool
    message_id: int
    sent_at: str
    delete_at: str
    chat_id: str


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str