from fastapi import FastAPI, APIRouter, HTTPException, Query
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
OTP_GATEWAY_URL = os.environ.get('OTP_GATEWAY_URL', 'http://localhost:55551')

# Magic Link Configuration
MAGIC_LINK_SECRET = os.environ.get('MAGIC_LINK_SECRET', 'your-magic-link-secret-change-in-production')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:55553", "http://localhost:80", "https://putana.date"],
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
    telegram_chat_id: Optional[str] = None
    telegram_username: Optional[str] = None

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
otp_history = []  # Store OTP history for admin UI

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

# Telegram Username Resolution
async def resolve_telegram_username(username: str) -> Optional[str]:
    """Resolve @username to Chat ID using Telegram Bot API"""
    try:
        # Remove @ if present
        if username.startswith('@'):
            username = username[1:]
        
        # For now, we'll use a simple approach
        # In production, you'd use the Telegram Bot API to get user info
        # This is a placeholder - you'd need to implement proper username resolution
        # using the Telegram Bot API with your bot token
        
        # For demo purposes, we'll return a mock chat ID
        # In real implementation, you'd call Telegram API here
        return "415043706"  # Mock chat ID for demo
        
    except Exception as e:
        logging.error(f"Failed to resolve username {username}: {e}")
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
            
        print(f"DEBUG: Sending OTP to {OTP_GATEWAY_URL}/send-otp with payload: {payload}")
        logging.info(f"Sending OTP to {OTP_GATEWAY_URL}/send-otp with payload: {payload}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OTP_GATEWAY_URL}/send-otp",
                json=payload,
                timeout=60.0
            )
            print(f"DEBUG: OTP Gateway response: {response.status_code} - {response.text}")
            logging.info(f"OTP Gateway response: {response.status_code} - {response.text}")
            
            # Record OTP history for admin UI
            if response.status_code == 200:
                otp_entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "chat_id": chat_id,
                    "otp": otp,
                    "email": email,
                    "status": "sent",
                    "message_id": response.json().get("message_id") if response.text else None
                }
                otp_history.append(otp_entry)
                # Keep only last 100 entries to prevent memory issues
                if len(otp_history) > 100:
                    otp_history.pop(0)
            
            return response.status_code == 200
    except Exception as e:
        print(f"DEBUG: Failed to send OTP via Telegram: {e}")
        logging.error(f"Failed to send OTP via Telegram: {e}")
        return False

def create_magic_link_token(email: str, otp: str) -> Optional[str]:
    """Create a magic link token with email, OTP, timestamp, and signature"""
    try:
        import time
        import hmac
        import hashlib
        import base64
        
        # Create token data
        token_time = str(int(time.time()))
        token_data = f"{email}:{otp}:{token_time}"
        
        # Create signature
        signature = hmac.new(
            MAGIC_LINK_SECRET.encode(),
            token_data.encode(),
            hashlib.sha256
        ).digest()
        
        # Combine data and signature
        full_token = f"{token_data}:{base64.urlsafe_b64encode(signature).decode()}"
        
        # Encode to base64 URL-safe
        token = base64.urlsafe_b64encode(full_token.encode()).decode()
        
        return token
    except Exception as e:
        logging.error(f"Failed to create magic link token: {e}")
        return None

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
        
        if not hmac.compare_digest(expected_signature, base64.urlsafe_b64decode(signature)):
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

@api_router.get("/status")
async def get_status():
    """Get system status for admin UI"""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "backend": "healthy",
            "otp_gateway": "healthy",
            "mongodb": "healthy"  # We're using file-based storage, but admin UI expects this
        },
        "version": "2.6.0"
    }

@api_router.post("/status")
async def create_status_check(input: StatusCheckCreate):
    """Create status check entry for admin UI"""
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Store in memory (simulating database)
    status_checks = getattr(create_status_check, 'status_checks', [])
    if not hasattr(create_status_check, 'status_checks'):
        create_status_check.status_checks = []
    
    create_status_check.status_checks.append(status_obj.model_dump())
    
    return status_obj

@api_router.get("/otp-history")
async def get_otp_history():
    """Get OTP history for admin UI"""
    return {
        "otp_history": otp_history[-10:],  # Last 10 entries
        "total_count": len(otp_history)
    }

@api_router.get("/history")
async def get_history():
    """Get general history for admin UI"""
    return {
        "otp_history": otp_history[-10:],  # Last 10 entries
        "total_count": len(otp_history),
        "recent_registrations": len(registration_sessions),
        "total_users": len(users_db)
    }

@api_router.post("/register")
async def register_user(registration: UserRegistration):
    """Start user registration process and send OTP"""
    if registration.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Validate that either chat_id or username is provided
    if not registration.telegram_chat_id and not registration.telegram_username:
        raise HTTPException(status_code=400, detail="Either telegram_chat_id or telegram_username is required")
    
    # Resolve username to chat_id if needed
    chat_id = registration.telegram_chat_id
    if not chat_id and registration.telegram_username:
        chat_id = await resolve_telegram_username(registration.telegram_username)
        if not chat_id:
            raise HTTPException(status_code=400, detail="Could not resolve Telegram username")
    
    import random
    otp = str(random.randint(100000, 999999))
    print(f"Generated OTP for {registration.email}: {otp}")  # For testing
    
    session_data = {
        "id": str(uuid.uuid4()),
        "email": registration.email,
        "user_data": registration.model_dump(),
        "otp": otp,
        "otp_sent": False,
        "resolved_chat_id": chat_id,  # Store the resolved chat_id
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }
    
    registration_sessions[registration.email] = session_data
    
    print(f"DEBUG: Attempting to send OTP via Telegram to chat_id: {chat_id}")
    logging.info(f"Attempting to send OTP via Telegram to chat_id: {chat_id}")
    otp_sent = await send_otp_via_telegram(chat_id, otp, registration.email)
    print(f"DEBUG: OTP sending result: {otp_sent}")
    logging.info(f"OTP sending result: {otp_sent}")
    
    if not otp_sent:
        # KISS: For testing, return OTP in response when Telegram fails
        registration_sessions[registration.email]["otp_sent"] = False
        return {
            "message": "Registration initiated. OTP sending failed, but you can use this OTP for testing:",
            "otp": otp,
            "warning": "OTP Gateway is not available - this is for testing only"
        }
    
    registration_sessions[registration.email]["otp_sent"] = True
    
    return {"message": "Registration initiated. Check your Telegram for OTP code and QR code!"}

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
    
    # Create magic link token instead of directly creating user
    user_data = session["user_data"]
    # Use resolved chat_id from session if available, otherwise use the original chat_id
    chat_id = session.get("resolved_chat_id") or user_data.get("telegram_chat_id")
    if not chat_id:
        raise HTTPException(status_code=400, detail="Telegram chat ID not found")
    
    # Create magic link token
    magic_link_token = create_magic_link_token(verification.email, verification.otp)
    if not magic_link_token:
        raise HTTPException(status_code=500, detail="Failed to create magic link")
    
    # Return magic link URL instead of direct success
    magic_link_url = f"https://putana.date/api/verify-magic-link?token={magic_link_token}"
    
    return {
        "message": "OTP verified successfully. Please check your email for the magic link.",
        "magic_link": magic_link_url,
        "token": magic_link_token
    }

@api_router.post("/resend-otp")
async def resend_otp(request: dict):
    """Resend OTP for existing registration session"""
    email = request.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    if email not in registration_sessions:
        raise HTTPException(status_code=400, detail="No registration session found")
    
    session = registration_sessions[email]
    
    # Generate new OTP
    import random
    new_otp = str(random.randint(100000, 999999))
    session["otp"] = new_otp
    
    # Send new OTP
    otp_sent = await send_otp_via_telegram(session["user_data"]["telegram_chat_id"], new_otp, email)
    
    if not otp_sent:
        # KISS: For testing, return OTP in response when Telegram fails
        return {
            "message": "OTP resend failed, but you can use this OTP for testing:",
            "otp": new_otp,
            "warning": "OTP Gateway is not available - this is for testing only"
        }
    
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

@api_router.get("/verify-magic-link")
async def verify_magic_link(token: str = Query(...)):
    """Verify magic link and complete registration"""
    from fastapi.responses import HTMLResponse
    
    # Verify the magic link token
    token_data = verify_magic_link_token(token)
    if not token_data:
        error_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Invalid Magic Link - Telega2Go</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; background-color: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
                .error { color: #dc3545; font-size: 24px; margin-bottom: 20px; }
                .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">❌ Invalid or Expired Magic Link</div>
                <h2>This magic link is invalid or has expired.</h2>
                <p>Please request a new registration or contact support if you continue to have issues.</p>
                <a href="/" class="btn">Go to Registration</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)
    
    email = token_data["email"]
    otp = token_data["otp"]
    
    # Check if registration session exists
    if email not in registration_sessions:
        error_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Session Not Found - Telega2Go</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; background-color: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
                .error { color: #dc3545; font-size: 24px; margin-bottom: 20px; }
                .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">❌ Registration Session Not Found</div>
                <h2>This magic link has already been used or the session has expired.</h2>
                <p>Please start a new registration process.</p>
                <a href="/" class="btn">Start New Registration</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)
    
    session = registration_sessions[email]
    
    # Verify OTP matches
    if session["otp"] != otp:
        error_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Invalid OTP - Telega2Go</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; background-color: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
                .error { color: #dc3545; font-size: 24px; margin-bottom: 20px; }
                .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">❌ Invalid OTP</div>
                <h2>The OTP in this magic link is invalid.</h2>
                <p>Please request a new registration or contact support.</p>
                <a href="/" class="btn">Start New Registration</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)
    
    # Check if session is not expired
    expires_at = datetime.fromisoformat(session["expires_at"].replace('Z', '+00:00'))
    if datetime.now(timezone.utc) > expires_at:
        error_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Session Expired - Telega2Go</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; background-color: #f5f5f5; }
                .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
                .error { color: #dc3545; font-size: 24px; margin-bottom: 20px; }
                .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error">❌ Session Expired</div>
                <h2>This registration session has expired.</h2>
                <p>Please start a new registration process.</p>
                <a href="/" class="btn">Start New Registration</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)
    
    # Create user
    user_data = session["user_data"]
    # Use resolved chat_id from session if available, otherwise use the original chat_id
    chat_id = session.get("resolved_chat_id") or user_data.get("telegram_chat_id")
    if not chat_id:
        raise HTTPException(status_code=400, detail="Telegram chat ID not found")
    
    user = User(
        name=user_data["name"],
        email=user_data["email"],
        phone=user_data["phone"],
        telegram_chat_id=chat_id,
        is_verified=True
    )
    
    users_db[email] = user
    
    # Generate JWT token
    access_token = create_access_token({"sub": user.email, "user_id": user.id})
    
    # Clean up registration session
    del registration_sessions[email]
    
    # Return HTML page instead of JSON
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Registration Successful - Telega2Go</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .success {{
                color: #28a745;
                font-size: 24px;
                margin-bottom: 20px;
            }}
            .user-info {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                text-align: left;
            }}
            .token {{
                background: #e9ecef;
                padding: 10px;
                border-radius: 5px;
                font-family: monospace;
                word-break: break-all;
                margin: 10px 0;
            }}
            .btn {{
                background: #007bff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success">✅ Registration Successful!</div>
            <h2>Welcome to Telega2Go, {user.name}!</h2>
            
            <div class="user-info">
                <h3>Your Account Details:</h3>
                <p><strong>Name:</strong> {user.name}</p>
                <p><strong>Email:</strong> {user.email}</p>
                <p><strong>Phone:</strong> {user.phone}</p>
                <p><strong>Telegram Chat ID:</strong> {user.telegram_chat_id}</p>
                <p><strong>Status:</strong> ✅ Verified</p>
                <p><strong>Registered:</strong> {user.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            
            <div class="user-info">
                <h3>Your Access Token:</h3>
                <div class="token">{access_token}</div>
                <p><small>Keep this token secure. It expires in 24 hours.</small></p>
            </div>
            
            <a href="/" class="btn">Go to Dashboard</a>
            <a href="/admin" class="btn">Admin Panel</a>
        </div>
    </body>
    </html>
    """
    
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content, status_code=200)

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
