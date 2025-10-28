from fastapi import FastAPI, APIRouter, HTTPException
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from jose import jwt
import httpx
import hmac
import hashlib
import base64

ROOT_DIR = Path(__file__).parent

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# OTP Gateway URL
OTP_GATEWAY_URL = os.environ.get('OTP_GATEWAY_URL', 'http://localhost:5571')

# Magic Link Configuration
MAGIC_LINK_SECRET = os.environ.get('MAGIC_LINK_SECRET', 'your-magic-link-secret-change-in-production')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5573", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# User Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    phone: str
    telegram_chat_id: str
    is_verified: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegistration(BaseModel):
    name: str
    email: EmailStr
    phone: str
    telegram_chat_id: str

class OTPVerification(BaseModel):
    email: EmailStr
    otp: str

class UserLogin(BaseModel):
    email: EmailStr
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    telegram_chat_id: str
    is_verified: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class RegistrationSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    user_data: dict
    otp_sent: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(hour=datetime.now(timezone.utc).hour + 1))

# In-memory storage for demo purposes
users_db = {}
registration_sessions = {}

# JWT Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# OTP Gateway Integration
async def send_otp_via_telegram(chat_id: str, otp: str, email: str = None) -> bool:
    """Send OTP via Telegram using the OTP Gateway"""
    try:
        payload = {
            "chat_id": chat_id,
            "otp": otp,
            "expire_seconds": 60  # 1 minute
        }
        if email:
            payload["email"] = email
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OTP_GATEWAY_URL}/send-otp",
                json=payload,
                timeout=30.0
            )
            return response.status_code == 200
    except Exception as e:
        logging.error(f"Failed to send OTP via Telegram: {e}")
        return False

def verify_magic_link_token(token: str) -> Optional[dict]:
    """Verify and decode magic link token"""
    try:
        # Decode the token
        decoded_token = base64.urlsafe_b64decode(token.encode()).decode()
        token_data, signature = decoded_token.rsplit(':', 1)
        
        # Verify signature
        expected_signature = hmac.new(
            MAGIC_LINK_SECRET.encode(),
            token_data.encode(),
            hashlib.sha256
        ).digest()
        
        provided_signature = base64.urlsafe_b64decode(signature.encode())
        
        if not hmac.compare_digest(expected_signature, provided_signature):
            return None
        
        # Parse token data
        email, otp, timestamp = token_data.split(':')
        
        # Check if token is not too old (1 hour)
        token_time = datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
        if datetime.now(timezone.utc) - token_time > timedelta(hours=1):
            return None
        
        return {
            "email": email,
            "otp": otp,
            "timestamp": token_time
        }
    except Exception as e:
        logging.error(f"Magic link token verification failed: {e}")
        return None

# API Endpoints
@api_router.get("/")
async def root():
    """Root endpoint for API health check"""
    return {"message": "Hello World"}

@api_router.post("/register")
async def register_user(registration: UserRegistration):
    """Start user registration process and send OTP"""
    if registration.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    import random
    otp = str(random.randint(100000, 999999))
    print(f"Generated OTP for {registration.email}: {otp}")  # For testing
    
    session_data = {
        "id": str(uuid.uuid4()),
        "email": registration.email,
        "user_data": registration.model_dump(),
        "otp": otp,
        "otp_sent": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": datetime.now(timezone.utc).replace(hour=datetime.now(timezone.utc).hour + 1).isoformat()
    }
    
    registration_sessions[registration.email] = session_data
    
    otp_sent = await send_otp_via_telegram(registration.telegram_chat_id, otp, registration.email)
    
    if not otp_sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP via Telegram")
    
    registration_sessions[registration.email]["otp_sent"] = True
    
    return {"message": "Registration initiated. Check your Telegram for OTP code."}

@api_router.post("/verify-otp")
async def verify_otp(verification: OTPVerification):
    """Verify OTP and complete user registration"""
    if verification.email not in registration_sessions:
        raise HTTPException(status_code=400, detail="No registration session found")
    
    session = registration_sessions[verification.email]
    
    if session["otp"] != verification.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Check if OTP has expired
    expires_at = datetime.fromisoformat(session["expires_at"].replace('Z', '+00:00'))
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="OTP has expired")
    
    # Create user
    user_data = session["user_data"]
    user = User(
        id=str(uuid.uuid4()),
        name=user_data["name"],
        email=user_data["email"],
        phone=user_data["phone"],
        telegram_chat_id=user_data["telegram_chat_id"],
        is_verified=True
    )
    
    users_db[verification.email] = user.model_dump()
    
    # Clean up session
    del registration_sessions[verification.email]
    
    # Create JWT token
    access_token = create_access_token({"sub": user.email, "user_id": user.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            telegram_chat_id=user.telegram_chat_id,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
    )

@api_router.post("/resend-otp")
async def resend_otp(email: str):
    """Resend OTP for existing registration session"""
    if email not in registration_sessions:
        raise HTTPException(status_code=400, detail="No registration session found")
    
    session = registration_sessions[email]
    
    # Generate new OTP
    import random
    new_otp = str(random.randint(100000, 999999))
    session["otp"] = new_otp
    
    # Send new OTP
    otp_sent = await send_otp_via_telegram(session["user_data"]["telegram_chat_id"], new_otp)
    
    if not otp_sent:
        raise HTTPException(status_code=500, detail="Failed to resend OTP via Telegram")
    
    return {"message": "OTP resent successfully"}

@api_router.get("/profile")
async def get_profile(token: str = None):
    """Get user profile (requires authentication)"""
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_email = payload.get("sub")
    if user_email not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_data = users_db[user_email]
    return UserResponse(
        id=user_data["id"],
        name=user_data["name"],
        email=user_data["email"],
        phone=user_data["phone"],
        telegram_chat_id=user_data["telegram_chat_id"],
        is_verified=user_data["is_verified"],
        created_at=datetime.fromisoformat(user_data["created_at"].replace('Z', '+00:00'))
    )

@api_router.post("/verify-magic-link")
async def verify_magic_link(token: str):
    """Verify magic link and complete registration"""
    # Verify the magic link token
    token_data = verify_magic_link_token(token)
    if not token_data:
        raise HTTPException(status_code=400, detail="Invalid or expired magic link")
    
    email = token_data["email"]
    otp = token_data["otp"]
    
    # Check if registration session exists
    if email not in registration_sessions:
        raise HTTPException(status_code=400, detail="No registration session found")
    
    session = registration_sessions[email]
    
    # Verify OTP matches
    if session["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP in magic link")
    
    # Check if session is not expired
    expires_at = datetime.fromisoformat(session["expires_at"].replace('Z', '+00:00'))
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Registration session expired")
    
    # Create user
    user_data = session["user_data"]
    user = User(
        name=user_data["name"],
        email=user_data["email"],
        phone=user_data["phone"],
        telegram_chat_id=user_data["telegram_chat_id"],
        is_verified=True
    )
    
    users_db[email] = user
    
    # Generate JWT token
    access_token = create_access_token({"sub": user.email, "user_id": user.id})
    
    # Clean up registration session
    del registration_sessions[email]
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "telegram_chat_id": user.telegram_chat_id,
            "is_verified": user.is_verified,
            "created_at": user.created_at
        }
    }

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
