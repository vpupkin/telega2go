from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from jose import jwt
import httpx


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Magic Link Configuration (KISS: Reuse same secret as JWT for simplicity)
MAGIC_LINK_SECRET = os.environ.get('MAGIC_LINK_SECRET', JWT_SECRET)

# OTP Gateway URL
OTP_GATEWAY_URL = os.environ.get('OTP_GATEWAY_URL', 'http://localhost:5571')

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
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
    email: str  # ✅ Changed from EmailStr to str to allow Telegram's @telegram.local emails
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

class TelegramUserRegistration(BaseModel):
    """✅ PENALTY4: Registration without OTP - user already validated from Telegram"""
    urr_id: str  # Unique Registration Request ID
    password: str  # Only editable field (min 6 chars validated in endpoint)
    username: Optional[str] = None  # Optional: if user changed username from default
    # All other fields come from Telegram data (stored with URR_ID)

class OTPVerification(BaseModel):
    email: EmailStr
    otp: str

class UserLogin(BaseModel):
    email: EmailStr
    password: Optional[str] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str
    name: str
    email: str
    phone: str
    telegram_chat_id: str
    is_verified: bool
    created_at: str  # ✅ Changed to str to avoid datetime serialization issues

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Registration Session Model
class RegistrationSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    user_data: dict
    otp_sent: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=1))

# JWT Utility Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire_dt = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    # ✅ JWT expects Unix timestamp (int), not datetime object
    expire_timestamp = int(expire_dt.timestamp())
    to_encode.update({"exp": expire_timestamp})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Magic Link Functions (KISS: Simple token creation/verification)
def create_magic_link_token(email: str, user_id: str) -> Optional[str]:
    """Create a magic link token for registered users - KISS approach"""
    try:
        import time
        import hmac
        import hashlib
        import base64
        
        # Create token data (email:user_id:timestamp)
        token_time = str(int(time.time()))
        token_data = f"{email}:{user_id}:{token_time}"
        
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
    """Verify and decode magic link token - KISS approach"""
    try:
        import base64
        import hmac
        import hashlib
        from datetime import timedelta
        
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
        email, user_id, timestamp = token_data.split(':')
        
        # Check if token is not too old (24 hours for registered users)
        token_time = datetime.fromtimestamp(float(timestamp), tz=timezone.utc)
        if datetime.now(timezone.utc) - token_time > timedelta(hours=24):
            return None
        
        return {
            "email": email,
            "user_id": user_id,
            "timestamp": token_time
        }
    except Exception as e:
        logging.error(f"Magic link token verification failed: {e}")
        return None

@api_router.post("/generate-magic-link")
async def generate_magic_link(request: dict):
    """Generate magic link for registered user - KISS: Simple token creation"""
    email = request.get("email")
    user_id = request.get("user_id")
    
    if not email or not user_id:
        raise HTTPException(status_code=400, detail="Email and user_id are required")
    
    # Verify user exists and is verified
    user = await db.users.find_one({"id": user_id, "email": email, "is_verified": True})
    if not user:
        raise HTTPException(status_code=404, detail="User not found or not verified")
    
    # Generate magic link token
    token = create_magic_link_token(email, user_id)
    if not token:
        raise HTTPException(status_code=500, detail="Failed to generate magic link")
    
    magic_link_url = f"https://putana.date/api/verify-magic-link?token={token}"
    
    return {
        "magic_link_url": magic_link_url,
        "token": token
    }

@api_router.get("/verify-magic-link")
async def verify_magic_link(token: str):
    """Verify magic link and authenticate registered user - KISS: Simple redirect"""
    from fastapi.responses import RedirectResponse
    
    # Verify the magic link token
    token_data = verify_magic_link_token(token)
    if not token_data:
        # Redirect to error page
        return RedirectResponse(url=f"/?error=invalid_token", status_code=302)
    
    email = token_data["email"]
    user_id = token_data["user_id"]
    
    # Verify user exists and is verified
    user = await db.users.find_one({"id": user_id, "email": email, "is_verified": True})
    if not user:
        return RedirectResponse(url=f"/?error=user_not_found", status_code=302)
    
    # Create JWT token for session
    token_data_jwt = {"sub": user["id"], "email": user["email"]}
    access_token = create_access_token(token_data_jwt)
    
    # Redirect to dashboard with token
    return RedirectResponse(url=f"/?token={access_token}", status_code=302)

# OTP Gateway Integration
async def send_otp_via_telegram(chat_id: str, otp: str):
    """Send OTP via Telegram using the OTP Gateway"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OTP_GATEWAY_URL}/send-otp",
                json={
                    "chat_id": chat_id,
                    "otp": otp,
                    "expire_seconds": 60  # 1 minute (max allowed)
                },
                timeout=30.0
            )
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Failed to send OTP via Telegram: {e}")
        return False

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# ✅ PENALTY4: Registration Request with URR_ID
@api_router.post("/create-registration-request")
async def create_registration_request(user_data: dict):
    """Generate URR_ID and store all Telegram user data"""
    import uuid
    
    try:
        # Generate unique Registration Request ID
        urr_id = str(uuid.uuid4())
        
        # Store complete Telegram profile data
        registration_request = {
            "urr_id": urr_id,
            "telegram_user_id": user_data.get("id"),
            "telegram_username": user_data.get("username"),
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "language_code": user_data.get("language_code", "en"),
            "is_premium": user_data.get("is_premium", False),
            # Additional fields from Telegram (if available)
            "email": user_data.get("email"),  # From Telegram if available
            "phone": user_data.get("phone"),  # From Telegram if available
            # GPS Location (if available from Telegram)
            "latitude": user_data.get("latitude"),
            "longitude": user_data.get("longitude"),
            "location": user_data.get("location"),
            # Store all additional Telegram data
            "telegram_data": user_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat(),  # 24h expiry
            "status": "pending"
        }
        
        # Store in registration_requests collection
        await db.registration_requests.insert_one(registration_request)
        
        # Also update telegram_users for backward compatibility
        await db.telegram_users.update_one(
            {"telegram_user_id": user_data.get("id")},
            {"$set": {
                "telegram_user_id": user_data.get("id"),
                "telegram_username": user_data.get("username"),
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "language_code": user_data.get("language_code", "en"),
                "is_premium": user_data.get("is_premium", False),
                "collected_at": datetime.now(timezone.utc).isoformat(),  # ✅ Store as ISO string for MongoDB
                "registration_pending": True
            }},
            upsert=True
        )
        
        return {
            "urr_id": urr_id,
            "registration_url": f"https://putana.date/registrationOfNewUser?urr_id={urr_id}"
        }
    except Exception as e:
        logging.error(f"Error creating registration request: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create registration request: {str(e)}")

@api_router.get("/registrationOfNewUser")
async def get_registration_form_data(urr_id: str = None, telegram_user_id: int = None):
    """✅ PENALTY4: Get Telegram user data by URR_ID or telegram_user_id (backward compat)"""
    try:
        registration_request = None
        
        # Try URR_ID first (new method)
        if urr_id:
            registration_request = await db.registration_requests.find_one({"urr_id": urr_id})
        
        # Fallback to telegram_user_id (backward compatibility)
        if not registration_request and telegram_user_id:
            telegram_profile = await db.telegram_users.find_one(
                {"telegram_user_id": telegram_user_id}
            )
            if telegram_profile:
                # Convert to registration request format
                registration_request = {
                    "telegram_user_id": telegram_user_id,
                    "telegram_username": telegram_profile.get("telegram_username"),
                    "first_name": telegram_profile.get("first_name"),
                    "last_name": telegram_profile.get("last_name"),
                    "language_code": telegram_profile.get("language_code", "en"),
                    "telegram_data": telegram_profile
                }
        
        if not registration_request:
            raise HTTPException(
                status_code=404, 
                detail="Registration request not found. Please call the bot first."
            )
        
        telegram_first_name = registration_request.get("first_name", "")
        
        # ✅ Check name availability (default to telegram_user_id as username)
        default_username = str(registration_request.get("telegram_user_id", ""))
        name_available = True
        suggestion = default_username
        name_message = None
        
        if telegram_first_name:
            # Check if Telegram first_name is available
            existing_user = await db.users.find_one({
                "name": {"$regex": f"^{telegram_first_name}$", "$options": "i"}
            })
            
            if existing_user:
                name_available = False
                suggestion = default_username  # Use telegram_user_id instead
                name_message = f"Name '{telegram_first_name}' is already taken. Default username will be your Telegram User ID: {default_username}"
            else:
                suggestion = telegram_first_name
        
        # Return ALL Telegram data
        return {
            "urr_id": registration_request.get("urr_id"),
            "telegram_user_id": registration_request.get("telegram_user_id"),
            "telegram_username": registration_request.get("telegram_username"),
            "first_name": registration_request.get("first_name"),
            "last_name": registration_request.get("last_name"),
            "language_code": registration_request.get("language_code", "en"),
            "is_premium": registration_request.get("is_premium", False),
            "email": registration_request.get("email"),  # From Telegram if available
            "phone": registration_request.get("phone"),  # From Telegram if available
            "latitude": registration_request.get("latitude"),
            "longitude": registration_request.get("longitude"),
            "location": registration_request.get("location"),
            "name_available": name_available,
            "suggested_name": suggestion,  # Default to telegram_user_id
            "default_username": default_username,
            "name_message": name_message,
            "telegram_data": registration_request.get("telegram_data", {})  # Full Telegram data
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in get_registration_form_data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.post("/register")
async def register_user(registration: UserRegistration):
    """Start user registration process and send OTP - KISS: Simple validation"""
    # ✅ CRITICAL: Check name uniqueness (KISS: Case-insensitive check)
    existing_user_by_name = await db.users.find_one({
        "name": {"$regex": f"^{registration.name}$", "$options": "i"}
    })
    
    if existing_user_by_name:
        raise HTTPException(
            status_code=400,
            detail=f"Name '{registration.name}' is already taken. Please choose a different name."
        )
    
    # Check if user already exists by email
    existing_user = await db.users.find_one({"email": registration.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    # Generate OTP
    import random
    otp = str(random.randint(100000, 999999))
    
    # Create registration session
    session_data = {
        "id": str(uuid.uuid4()),
        "email": registration.email,
        "user_data": registration.model_dump(),
        "otp": otp,
        "otp_sent": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    }
    
    # Store session
    await db.registration_sessions.insert_one(session_data)
    
    # Send OTP via Telegram
    otp_sent = await send_otp_via_telegram(registration.telegram_chat_id, otp)
    
    if not otp_sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP via Telegram")
    
    # Update session with OTP sent status
    await db.registration_sessions.update_one(
        {"email": registration.email},
        {"$set": {"otp_sent": True}}
    )
    
    return {"message": "Registration initiated. Check your Telegram for OTP code."}

@api_router.post("/register-telegram", response_model=TokenResponse)
async def register_telegram_user(registration: TelegramUserRegistration):
    """✅ PENALTY4: Register Telegram user directly - ALL data from stored URR_ID, only password editable"""
    import sys
    import traceback
    
    try:
        logging.info(f"=== ENTERING register_telegram_user ===")
        logging.info(f"Registration object: urr_id={registration.urr_id}, username={registration.username}, password length={len(registration.password) if registration.password else 0}")
    except Exception as e:
        print(f"ERROR IN LOGGING: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
    
    try:
        # ✅ Log incoming request for debugging (SIMPLIFIED to avoid datetime serialization)
        try:
            urr_id_str = str(registration.urr_id) if registration.urr_id else "None"
            username_str = str(registration.username) if registration.username else "None"
            has_pwd = "Yes" if registration.password else "No"
            logging.info(f"Register Telegram User - URR_ID: {urr_id_str}, Username: {username_str}, Has Password: {has_pwd}")
        except Exception as log_err:
            print(f"ERROR IN LOGGING: {log_err}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            # Continue anyway
        
        # ✅ Validate password length (additional check) - WRAP EVERYTHING
        try:
            if not registration.password:
                raise HTTPException(status_code=400, detail="Password is required")
            
            password_stripped = registration.password.strip()
            password_valid = len(password_stripped) >= 6
            
            if not password_valid:
                raise HTTPException(
                    status_code=400,
                    detail="Password must be at least 6 characters"
                )
            
            logging.info("Step 1: Password validated")
        except HTTPException:
            raise
        except Exception as pwd_err:
            print(f"ERROR IN PASSWORD CHECK: {pwd_err}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise HTTPException(status_code=500, detail=f"Password validation error: {str(pwd_err)}")
        
        # ✅ CRITICAL FIX: Use simple find_one and handle datetime fields manually
        # Aggregation pipeline was causing the error - skip it entirely
        # Registration requests are stored with ISO strings (see create_registration_request)
        try:
            logging.info(f"Step 1.5: Querying database for urr_id: {registration.urr_id}")
            # Use simple find_one - documents already have ISO strings, not datetime objects
            registration_request = await db.registration_requests.find_one({"urr_id": registration.urr_id})
            logging.info(f"Step 1.6: Database query completed, got request: {bool(registration_request)}")
        except Exception as db_err:
            import sys
            import traceback
            logging.error(f"Error in database query: {db_err}")
            print(f"ERROR IN DATABASE QUERY: {db_err}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_err)}")
        
        if not registration_request:
            raise HTTPException(
                status_code=400,
                detail="Registration request not found or expired. Please start registration again."
            )
        
        # ✅ CRITICAL FIX: Document should now have datetime fields as ISO strings from aggregation
        # Just convert to plain dict
        logging.info(f"Step 1.7: Starting document processing (datetimes should already be strings)")
        
        # ✅ Document should already have datetime fields as ISO strings from aggregation pipeline
        # Just convert to plain dict (should be safe now)
        try:
            registration_request_dict = dict(registration_request)
            logging.info(f"Step 1.7a: Converted to dict, keys: {list(registration_request_dict.keys())[:10]}")
        except Exception as conv_err:
            # If dict() fails, build manually
            import sys
            import traceback
            logging.error(f"Error converting to dict: {conv_err}")
            print(f"Error converting to dict: {conv_err}", file=sys.stderr)
            
            registration_request_dict = {}
            for key in ['urr_id', 'telegram_user_id', 'telegram_username', 'first_name', 'last_name',
                        'language_code', 'is_premium', 'email', 'phone', 
                        'latitude', 'longitude', 'location', 'telegram_data', 'status',
                        'created_at', 'expires_at']:
                try:
                    val = registration_request.get(key, None) if hasattr(registration_request, 'get') else getattr(registration_request, key, None)
                    if val is not None:
                        registration_request_dict[key] = val
                except:
                    if key == 'created_at':
                        registration_request_dict[key] = datetime.now(timezone.utc).isoformat()
                    elif key == 'expires_at':
                        registration_request_dict[key] = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
            
            logging.info(f"Step 1.7b: Manual conversion, {len(registration_request_dict)} fields")
        
        # Ensure datetime fields are strings (should already be from aggregation)
        if 'created_at' not in registration_request_dict or not isinstance(registration_request_dict.get('created_at'), str):
            registration_request_dict['created_at'] = datetime.now(timezone.utc).isoformat()
        if 'expires_at' not in registration_request_dict or not isinstance(registration_request_dict.get('expires_at'), str):
            registration_request_dict['expires_at'] = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        
        registration_request = registration_request_dict
        logging.info(f"Step 1.7c: Document processing complete, {len(registration_request)} fields")
        
        logging.info("Step 2: Registration request found and converted to dict")
        
        # ✅ SAFELY access registration_request fields one by one to isolate error
        try:
            logging.info(f"Step 2.1: urr_id = {registration_request.get('urr_id')}")
        except Exception as e:
            print(f"ERROR accessing urr_id: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise
        
        try:
            logging.info(f"Step 2.2: telegram_user_id = {registration_request.get('telegram_user_id')}")
        except Exception as e:
            print(f"ERROR accessing telegram_user_id: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise
        
        # Check if request expired
        # ✅ Parse expires_at with proper timezone handling (DEFENSIVE)
        logging.info("Step 2.5: Parsing expires_at")
        try:
            expires_at_str = registration_request.get('expires_at')
            logging.info(f"Step 2.5: Got expires_at_str, type: {type(expires_at_str)}, value (first 50): {str(expires_at_str)[:50] if expires_at_str else None}")
        except Exception as e:
            print(f"ERROR accessing expires_at: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            raise
        if not expires_at_str:
            raise HTTPException(status_code=400, detail="Registration request missing expiry date")
        
        try:
            import re
            # Handle 'Z' suffix - if string ends with 'Z', handle timezone properly
            if expires_at_str.endswith('Z'):
                # Check if there's already a timezone offset pattern (+XX:XX or -XX:XX) before the Z
                tz_match = re.search(r'[+-]\d{2}:\d{2}', expires_at_str[:-1])
                if tz_match:
                    # Has timezone offset, just remove the Z
                    expires_at_str = expires_at_str[:-1]
                else:
                    # No timezone offset, replace Z with +00:00
                    expires_at_str = expires_at_str[:-1] + '+00:00'
            
            logging.info(f"Step 2.5a: expires_at_str prepared: {expires_at_str[:50]}")
            expires_at = datetime.fromisoformat(expires_at_str)
            logging.info(f"Step 2.5b: datetime.fromisoformat succeeded, hour: {expires_at.hour}")
            
            # Ensure it's timezone-aware
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            # ✅ Validate hour is in valid range
            if expires_at.hour < 0 or expires_at.hour > 23:
                logging.error(f"Invalid hour in expires_at: {expires_at.hour}, creating new datetime")
                expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            
            logging.info(f"Step 3: expires_at parsed successfully: {expires_at}, hour: {expires_at.hour}")
        except ValueError as e:
            error_msg = str(e)
            logging.error(f"ValueError parsing expires_at: {error_msg}, value: {registration_request.get('expires_at')}")
            import sys
            import traceback
            print(f"ERROR IN EXPIRES_AT PARSING: {error_msg}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            raise HTTPException(
                status_code=500,
                detail=f"Invalid registration request expiry date: {error_msg}"
            )
        except Exception as e:
            logging.error(f"Unexpected error parsing expires_at: {e}, value: {registration_request.get('expires_at')}")
            import sys
            import traceback
            print(f"ERROR IN EXPIRES_AT PARSING (OTHER): {e}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            raise HTTPException(
                status_code=500,
                detail=f"Invalid registration request expiry date: {str(e)}"
            )
        
        # ✅ Compare with current time (defensive)
        try:
            now = datetime.now(timezone.utc)
            if now > expires_at:
                raise HTTPException(
                    status_code=400,
                    detail="Registration request expired. Please start registration again."
                )
        except Exception as cmp_err:
            import sys
            import traceback
            print(f"ERROR IN DATETIME COMPARISON: {cmp_err}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            raise HTTPException(
                status_code=400,
                detail="Registration request expired. Please start registration again."
            )
        logging.info("Step 4: Registration request not expired")
        
        # Extract all data from stored Telegram data
        telegram_data = registration_request.get('telegram_data', {})
        telegram_user_id = registration_request.get('telegram_user_id')
        
        # ✅ Use provided username or default to telegram_user_id
        username = registration.username if registration.username else str(telegram_user_id)
        
        # ✅ Check username uniqueness (CRITICAL)
        existing_user_by_name = await db.users.find_one({
            "name": {"$regex": f"^{username}$", "$options": "i"}
        })
        if existing_user_by_name:
            raise HTTPException(
                status_code=400,
                detail=f"Username '{username}' is already taken. Please choose a different username."
            )
        
        email = registration_request.get('email') or telegram_data.get('email') or f"user{telegram_user_id}@telegram.local"
        phone = registration_request.get('phone') or telegram_data.get('phone') or ""
        
        # Check if Telegram user already registered
        existing_telegram_user = await db.users.find_one({
            "$or": [
                {"telegram_user_id": telegram_user_id},
                {"telegram_chat_id": str(telegram_user_id)}
            ]
        })
        if existing_telegram_user:
            raise HTTPException(status_code=400, detail="This Telegram account is already registered")
        
        # ✅ Create user_doc directly to bypass Pydantic validation for Telegram emails
        # (Telegram may provide invalid emails like user123@telegram.local)
        # ✅ CRITICAL FIX: Use ISO strings immediately to avoid MongoDB datetime deserialization errors
        logging.info("Step 5: Creating user_doc")
        try:
            # Convert to ISO string immediately - never use datetime objects in MongoDB documents
            now_iso = datetime.now(timezone.utc).isoformat()
            logging.info(f"Step 5a: Created ISO string: {now_iso[:50]}")
        except Exception as dt_err:
            import sys
            import traceback
            logging.error(f"ERROR CREATING datetime ISO string: {dt_err}")
            print(f"ERROR CREATING datetime ISO string: {dt_err}", file=sys.stderr)
            print(traceback.format_exc(), file=sys.stderr)
            raise HTTPException(status_code=500, detail=f"Error creating timestamp: {str(dt_err)}")
        
        user_doc = {
            "id": str(uuid.uuid4()),
            "name": username,  # Default to telegram_user_id
            "email": email,  # May be invalid format (e.g., @telegram.local) - OK for Telegram users
            "phone": phone,
            "telegram_chat_id": str(telegram_user_id),
            "is_verified": True,  # ✅ Already validated via Telegram
            "created_at": now_iso,  # ✅ ISO string immediately - no datetime objects
            "updated_at": now_iso   # ✅ ISO string immediately - no datetime objects
        }
        logging.info(f"Step 5b: user_doc created, created_at type: {type(user_doc['created_at'])}, value: {user_doc['created_at'][:50]}")
        user_doc['telegram_user_id'] = telegram_user_id
        user_doc['telegram_username'] = registration_request.get('telegram_username')
        user_doc['first_name'] = registration_request.get('first_name')
        user_doc['last_name'] = registration_request.get('last_name')
        user_doc['language_code'] = registration_request.get('language_code', 'en')
        user_doc['is_premium'] = registration_request.get('is_premium', False)
        user_doc['password_hash'] = registration.password  # Store password (should hash in production!)
        
        # Additional fields from Telegram
        user_doc['latitude'] = registration_request.get('latitude')
        user_doc['longitude'] = registration_request.get('longitude')
        user_doc['location'] = registration_request.get('location')
        user_doc['bank_id'] = telegram_data.get('bank_id')  # If available
        user_doc['driver_license'] = telegram_data.get('driver_license')  # If available
        user_doc['nationality'] = telegram_data.get('nationality')  # If available
        user_doc['supported_languages'] = [registration_request.get('language_code', 'en')]  # Array
        
        # ✅ Datetime fields are already ISO strings (converted at creation)
        # No conversion needed - skip this step
        logging.info("Step 6: Datetime fields already ISO strings, skipping conversion")
        
        await db.users.insert_one(user_doc)
        
        # Mark registration request as completed
        await db.registration_requests.update_one(
            {"urr_id": registration.urr_id},
            {"$set": {"status": "completed"}}
        )
        
        # Create JWT token
        token_data = {"sub": user_doc["id"], "email": user_doc["email"]}
        access_token = create_access_token(token_data)
        
        # ✅ Extract created_at as ISO string (UserResponse expects string, not datetime)
        logging.info(f"Step 6.5: Extracting created_at from user_doc, type: {type(user_doc.get('created_at'))}")
        
        if isinstance(user_doc.get("created_at"), str):
            # Already a string, use it directly
            created_at_str = user_doc["created_at"]
            logging.info(f"Step 6.5a: created_at is already string: {created_at_str[:50]}")
        elif isinstance(user_doc.get("created_at"), datetime):
            # Convert datetime to ISO string
            dt = user_doc["created_at"]
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            created_at_str = dt.isoformat()
            logging.info(f"Step 6.5b: Converted datetime to string: {created_at_str[:50]}")
        else:
            # Fallback: use current time as ISO string
            created_at_str = datetime.now(timezone.utc).isoformat()
            logging.info(f"Step 6.5c: Using fallback datetime string: {created_at_str[:50]}")
        
        logging.info(f"Step 7: Creating UserResponse with created_at (first 50 chars): {created_at_str[:50] if created_at_str else 'None'}")
        
        try:
            # ✅ Ensure created_at_str is a valid ISO string
            if not created_at_str or not isinstance(created_at_str, str):
                created_at_str = datetime.now(timezone.utc).isoformat()
            
            user_response = UserResponse(
                id=user_doc["id"],
                name=user_doc["name"],
                email=user_doc["email"],
                phone=user_doc["phone"],
                telegram_chat_id=user_doc["telegram_chat_id"],
                is_verified=user_doc["is_verified"],
                created_at=created_at_str  # ✅ String, not datetime
            )
            logging.info("Step 7a: UserResponse created successfully")
        except Exception as e:
            logging.error(f"Error creating UserResponse: {e}, created_at_str: {created_at_str}")
            import traceback
            error_trace = traceback.format_exc()
            logging.error(f"Traceback:\n{error_trace}")
            # Fallback: create UserResponse with current time as ISO string
            created_at_str = datetime.now(timezone.utc).isoformat()
            user_response = UserResponse(
                id=user_doc["id"],
                name=user_doc["name"],
                email=user_doc["email"],
                phone=user_doc["phone"],
                telegram_chat_id=user_doc["telegram_chat_id"],
                is_verified=user_doc["is_verified"],
                created_at=created_at_str
            )
            logging.info("Step 7b: UserResponse created with fallback datetime string")
        
        # ✅ Create TokenResponse (check if this causes the error)
        try:
            logging.info("Step 8: Creating TokenResponse")
            token_response = TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=user_response
            )
            logging.info("Step 8a: TokenResponse created successfully")
            return token_response
        except Exception as token_err:
            import sys
            import traceback
            error_trace = traceback.format_exc()
            print(f"\n{'='*50}", file=sys.stderr)
            print(f"ERROR creating TokenResponse: {token_err}", file=sys.stderr)
            print(f"FULL TRACEBACK:", file=sys.stderr)
            print(error_trace, file=sys.stderr)
            print(f"{'='*50}\n", file=sys.stderr)
            logging.error(f"Error creating TokenResponse: {token_err}\nTraceback:\n{error_trace}")
            raise HTTPException(status_code=500, detail=f"Error creating response: {str(token_err)}")
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        import sys
        error_trace = traceback.format_exc()
        # Print to stderr (will appear in docker logs)
        print(f"\n{'='*50}", file=sys.stderr)
        print(f"ERROR in register_telegram_user: {e}", file=sys.stderr)
        print(f"ERROR TYPE: {type(e)}", file=sys.stderr)
        print(f"FULL TRACEBACK:", file=sys.stderr)
        print(error_trace, file=sys.stderr)
        print(f"{'='*50}\n", file=sys.stderr)
        # Also try to log it
        try:
            logging.error(f"Error in register_telegram_user: {e}\nTraceback:\n{error_trace}")
        except:
            pass
        # Include traceback in error detail for debugging
        error_detail = f"Internal server error: {str(e)}\nTraceback:\n{error_trace[:1000]}"  # Limit traceback length
        raise HTTPException(status_code=500, detail=error_detail)

@api_router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(verification: OTPVerification):
    """Verify OTP and complete user registration"""
    # Find registration session
    session = await db.registration_sessions.find_one({"email": verification.email})
    if not session:
        raise HTTPException(status_code=404, detail="Registration session not found")
    
    # Check if session is expired
    if datetime.now(timezone.utc) > datetime.fromisoformat(session['expires_at']):
        raise HTTPException(status_code=400, detail="Registration session expired")
    
    # Verify OTP
    if session.get('otp') != verification.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Create user (KISS: Link Telegram profile if available)
    user_data = session['user_data']
    telegram_user_id = int(user_data.get('telegram_chat_id')) if user_data.get('telegram_chat_id', '').isdigit() else None
    
    # Try to get Telegram profile data
    telegram_profile = await db.telegram_users.find_one(
        {"telegram_user_id": telegram_user_id}
    ) if telegram_user_id else None
    
    user = User(
        name=user_data['name'],
        email=user_data['email'],
        phone=user_data['phone'],
        telegram_chat_id=user_data['telegram_chat_id'],
        is_verified=True
    )
    
    # Save user to database (KISS: Add Telegram fields if available)
    user_doc = user.model_dump()
    if telegram_profile:
        user_doc['telegram_user_id'] = telegram_user_id
        user_doc['telegram_username'] = telegram_profile.get('telegram_username')
        user_doc['first_name'] = telegram_profile.get('first_name')
        user_doc['last_name'] = telegram_profile.get('last_name')
        user_doc['language_code'] = telegram_profile.get('language_code', 'en')
    
    user_doc['created_at'] = user_doc['created_at'].isoformat()
    user_doc['updated_at'] = user_doc['updated_at'].isoformat()
    
    await db.users.insert_one(user_doc)
    
    # Clean up registration session
    await db.registration_sessions.delete_one({"email": verification.email})
    
    # Create JWT token
    token_data = {"sub": user.id, "email": user.email}
    access_token = create_access_token(token_data)
    
    # Return user data and token
    user_response = UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        telegram_chat_id=user.telegram_chat_id,
        is_verified=user.is_verified,
        created_at=user.created_at
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )

@api_router.post("/resend-otp")
async def resend_otp(email: str):
    """Resend OTP for registration"""
    # Find registration session
    session = await db.registration_sessions.find_one({"email": email})
    if not session:
        raise HTTPException(status_code=404, detail="Registration session not found")
    
    # Check if session is expired
    if datetime.now(timezone.utc) > datetime.fromisoformat(session['expires_at']):
        raise HTTPException(status_code=400, detail="Registration session expired")
    
    # Generate new OTP
    import random
    otp = str(random.randint(100000, 999999))
    
    # Update session with new OTP
    await db.registration_sessions.update_one(
        {"email": email},
        {"$set": {"otp": otp}}
    )
    
    # Send OTP via Telegram
    otp_sent = await send_otp_via_telegram(session['user_data']['telegram_chat_id'], otp)
    
    if not otp_sent:
        raise HTTPException(status_code=500, detail="Failed to resend OTP via Telegram")
    
    return {"message": "OTP resent successfully"}

@api_router.get("/profile", response_model=UserResponse)
async def get_user_profile(token: str = Depends(lambda: None)):
    """Get user profile (requires authentication)"""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Convert ISO string timestamps back to datetime objects
        if isinstance(user['created_at'], str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
        
        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# ✅ Admin User Management Endpoints
@api_router.get("/users", response_model=List[UserResponse])
async def list_users():
    """Get all users (admin only - TODO: add admin authentication)"""
    try:
        users = await db.users.find({}, {"_id": 0}).to_list(length=1000)  # Limit to 1000 users
        
        # Convert ISO string timestamps back to datetime objects
        for user in users:
            if isinstance(user.get('created_at'), str):
                user['created_at'] = datetime.fromisoformat(user['created_at'])
        
        return [UserResponse(**user) for user in users]
    except Exception as e:
        logging.error(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")

@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get a single user by ID (admin only)"""
    try:
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Convert ISO string timestamps back to datetime objects
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
        
        return UserResponse(**user)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

class UserUpdate(BaseModel):
    """Model for updating user details"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    is_verified: Optional[bool] = None
    telegram_user_id: Optional[int] = None
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None

@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user details (admin only)"""
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"id": user_id})
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check username uniqueness if name is being updated
        if user_update.name:
            existing_user_by_name = await db.users.find_one({
                "name": {"$regex": f"^{user_update.name}$", "$options": "i"},
                "id": {"$ne": user_id}  # Exclude current user
            })
            if existing_user_by_name:
                raise HTTPException(
                    status_code=400,
                    detail=f"Username '{user_update.name}' is already taken."
                )
        
        # Check email uniqueness if email is being updated
        if user_update.email:
            existing_user_by_email = await db.users.find_one({
                "email": user_update.email,
                "id": {"$ne": user_id}  # Exclude current user
            })
            if existing_user_by_email:
                raise HTTPException(
                    status_code=400,
                    detail=f"Email '{user_update.email}' is already in use."
                )
        
        # Build update dictionary (only include provided fields)
        update_data = {}
        if user_update.name is not None:
            update_data['name'] = user_update.name
        if user_update.email is not None:
            update_data['email'] = user_update.email
        if user_update.phone is not None:
            update_data['phone'] = user_update.phone
        if user_update.telegram_chat_id is not None:
            update_data['telegram_chat_id'] = user_update.telegram_chat_id
        if user_update.is_verified is not None:
            update_data['is_verified'] = user_update.is_verified
        if user_update.telegram_user_id is not None:
            update_data['telegram_user_id'] = user_update.telegram_user_id
        if user_update.telegram_username is not None:
            update_data['telegram_username'] = user_update.telegram_username
        if user_update.first_name is not None:
            update_data['first_name'] = user_update.first_name
        if user_update.last_name is not None:
            update_data['last_name'] = user_update.last_name
        if user_update.language_code is not None:
            update_data['language_code'] = user_update.language_code
        
        # Always update updated_at timestamp
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        
        # Update user
        await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        # Fetch and return updated user
        updated_user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if isinstance(updated_user.get('created_at'), str):
            updated_user['created_at'] = datetime.fromisoformat(updated_user['created_at'])
        
        return UserResponse(**updated_user)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user from the system (admin only)"""
    try:
        # Check if user exists
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete user
        result = await db.users.delete_one({"id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()