"""FastAPI application for OTP Social Gateway"""
import asyncio
import logging
import sys
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from collections import defaultdict, deque
from time import time

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

from app.config import settings
from app.models import SendOTPRequest, SendOTPResponse, ErrorResponse, HealthResponse
from app.simple_otp_service import SimpleOTPService
from app.bot_commands import FunnyBotCommands
from app import __version__

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Prometheus metrics
otp_sent_counter = Counter('otp_sent_total', 'Total OTPs sent')
otp_failed_counter = Counter('otp_failed_total', 'Total OTP send failures')
rate_limit_exceeded_counter = Counter('rate_limit_exceeded_total', 'Total rate limit violations')

# In-memory rate limiting store
user_rate_limits = defaultdict(lambda: deque(maxlen=settings.rate_limit_per_user))

# Initialize OTP service
otp_service: SimpleOTPService = None
bot_commands: FunnyBotCommands = None


def check_user_rate_limit(chat_id: str) -> bool:
    """Check if user has exceeded rate limit"""
    current_time = time()
    window_start = current_time - (settings.rate_limit_window_hours * 3600)
    
    # Clean old timestamps
    user_timestamps = user_rate_limits[chat_id]
    while user_timestamps and user_timestamps[0] < window_start:
        user_timestamps.popleft()
    
    # Check if limit exceeded
    if len(user_timestamps) >= settings.rate_limit_per_user:
        return False
    
    # Add current timestamp
    user_timestamps.append(current_time)
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global otp_service
    
    # Startup
    logger.info("Starting OTP Social Gateway...")
    
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    
    global otp_service, bot_commands
    otp_service = SimpleOTPService(settings.telegram_bot_token)
    bot_commands = FunnyBotCommands(settings.telegram_bot_token)
    
    # Skip bot token verification due to persistent network timeouts
    logger.info("Skipping bot token verification due to network timeout issues")
    
    logger.info(f"OTP Social Gateway started on port {settings.port}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OTP Social Gateway...")


# Initialize FastAPI app with /otp/ prefix for Apache2 compatibility
app = FastAPI(
    title="OTP Social Gateway",
    description="Secure OTP delivery via Telegram with self-destructing messages",
    version=__version__,
    lifespan=lifespan,
    docs_url="/otp/docs",
    redoc_url="/otp/redoc",
    root_path="/otp"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:55553", "http://localhost:80", "https://putana.date"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "error": "Internal server error"}
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=__version__
    )


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    stats = otp_service.get_stats() if otp_service else {}
    return PlainTextResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.post(
    "/send-otp",
    response_model=SendOTPResponse,
    responses={
        200: {"model": SendOTPResponse},
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    tags=["OTP"]
)
@limiter.limit("10/minute")
async def send_otp(request: Request, otp_request: SendOTPRequest):
    """
    Send OTP to Telegram user with self-destruct timer
    
    - **chat_id**: Telegram user chat ID (numeric string)
    - **otp**: One-Time Password (4-8 digits)
    - **expire_seconds**: Auto-delete after seconds (5-60, default: 30)
    
    Returns message details including when it will be deleted.
    """
    # Check user-specific rate limit
    if not check_user_rate_limit(otp_request.chat_id):
        rate_limit_exceeded_counter.inc()
        logger.warning(
            f"Rate limit exceeded for user",
            extra={"chat_id": otp_request.chat_id}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Maximum {settings.rate_limit_per_user} OTPs per {settings.rate_limit_window_hours} hour(s)"
        )
    
    # Send OTP
    response_data = await otp_service.send_otp(
        chat_id=otp_request.chat_id,
        otp=otp_request.otp,
        expire_seconds=otp_request.expire_seconds or settings.default_expire_seconds,
        email=otp_request.email
    )
    success = response_data.get("success", False)
    
    if success:
        otp_sent_counter.inc()
        return SendOTPResponse(**response_data)
    else:
        otp_failed_counter.inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=response_data.get("details", "Failed to send OTP")
        )


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "OTP Social Gateway",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
        "webhook": "/webhook"
    }


@app.post("/webhook", tags=["Bot"])
async def telegram_webhook(request: Request):
    """
    Handle Telegram bot commands, messages, inline queries, and callback queries
    
    This endpoint receives updates from Telegram when users:
    - Send commands to the bot (/start, /help, etc.)
    - Mention the bot with @taxoin_bot (inline queries)
    - Click buttons in messages (callback queries)
    """
    try:
        data = await request.json()
        
        # Handle inline queries (when @taxoin_bot is typed)
        if "inline_query" in data:
            inline_query = data["inline_query"]
            inline_query_id = inline_query["id"]
            query = inline_query.get("query", "")
            user = inline_query.get("from", {})
            user_id = str(user.get("id", ""))
            language_code = user.get("language_code")  # Get user's Telegram language
            
            if bot_commands:
                success = await bot_commands.handle_inline_query(inline_query_id, query, user_id, language_code)
                if success:
                    logger.info(f"Handled inline query from user {user_id}")
                    return {"status": "success", "type": "inline_query"}
                else:
                    logger.error(f"Failed to handle inline query from user {user_id}")
                    return {"status": "error", "message": "Failed to process inline query"}
            else:
                logger.error("Bot commands not initialized")
                return {"status": "error", "message": "Bot commands not available"}
        
        # Handle callback queries (when buttons are clicked)
        if "callback_query" in data:
            callback_query = data["callback_query"]
            callback_query_id = callback_query["id"]
            callback_data = callback_query.get("data", "")
            message = callback_query.get("message", {})
            chat_id = str(message.get("chat", {}).get("id", ""))
            message_id = message.get("message_id", 0)
            user = callback_query.get("from", {})
            language_code = user.get("language_code")  # Get user's Telegram language
            
            if bot_commands:
                success = await bot_commands.handle_callback_query(
                    callback_query_id, chat_id, message_id, callback_data, language_code
                )
                if success:
                    logger.info(f"Handled callback query '{callback_data}' from chat {chat_id}")
                    return {"status": "success", "type": "callback_query"}
                else:
                    logger.error(f"Failed to handle callback query from chat {chat_id}")
                    return {"status": "error", "message": "Failed to process callback query"}
            else:
                logger.error("Bot commands not initialized")
                return {"status": "error", "message": "Bot commands not available"}
        
        # Check if it's a message update
        if "message" in data:
            message = data["message"]
            chat_id = str(message["chat"]["id"])
            text = message.get("text", "")
            user = message.get("from", {})
            username = user.get("username")
            language_code = user.get("language_code")  # Get user's Telegram language
            
            # Handle commands
            if text.startswith("/"):
                command = text.split()[0] if text.split() else text
                if bot_commands:
                    success = await bot_commands.handle_command(chat_id, command, username, language_code)
                else:
                    logger.error("Bot commands not initialized")
                    return {"status": "error", "message": "Bot commands not available"}
                
                if success:
                    logger.info(f"Handled command '{command}' for user {chat_id}")
                    return {"status": "success", "command": command}
                else:
                    logger.error(f"Failed to handle command '{command}' for user {chat_id}")
                    return {"status": "error", "message": "Failed to process command"}
            
            # Handle regular messages
            elif text:
                # Send a friendly response to regular messages
                responses = [
                    "Hey! I'm a bot, not a chat buddy! Try /help to see what I can do! 🤖",
                    "I only understand commands! Type /help to see my superpowers! ⚡",
                    "Commands only, please! I'm not here for small talk! /help 🎭",
                    "I'm a security bot, not a therapist! Use /help to see my commands! 🔐",
                    "Sorry, I only speak in commands! Try /joke for a laugh! 😄"
                ]
                
                import random
                response = random.choice(responses)
                if bot_commands:
                    await bot_commands.send_message(chat_id, response)
                else:
                    logger.error("Bot commands not initialized for regular message")
                return {"status": "success", "message": "Sent response"}
        
        return {"status": "ignored", "message": "Not a recognized update type"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}