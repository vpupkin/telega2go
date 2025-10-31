# TECHNICAL DOCUMENTATION - OTP Social Gateway

## 📚 **DOCUMENTATION INDEX**

### **Setup & Configuration**
- **[Telegram Inline Query Menu Setup](./TELEGRAM_INLINE_QUERY_MENU_SETUP.md)** - Complete guide for enabling and using inline query menu
- **[Development Rules](./A_DEVELOPMENT_RULES.md)** - Mandatory development workflow and rules
- **[Docker-Only Setup](./A_DOCKER_ONLY_SETUP.md)** - Docker deployment guide

### **Features**
- **[Funny Telegram Bot Commands](./FUNNY_TELEGRAM_BOT_COMMANDS_v2.8.0.md)** - Bot entertainment commands
- **[PWA User Registration System](./A_PWA_USER_REGISTRATION_SYSTEM.md)** - Registration system overview
- **[Magic Link Authentication](./MAGIC_LINK_AUTHENTICATION_v2.1.0.md)** - Magic link implementation

### **Telegram Bot Features**
- **[Inline Query Menu](./TELEGRAM_INLINE_QUERY_MENU_SETUP.md)** - Interactive menu via @bot_username
- **[Bot Commands](./FUNNY_TELEGRAM_BOT_COMMANDS_v2.8.0.md)** - /start, /help, /joke, etc.
- **[OTP Delivery](./OTP_QR_CODE_FIX_v2.6.0.md)** - QR code and OTP sending

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **Microservices Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │  OTP Gateway    │
│   (React)       │◄──►│   (FastAPI)     │    │   (FastAPI)     │
│   Port: 5573    │    │   Port: 5572    │    │   Port: 5571    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │    MongoDB      │
                    │   Port: 5574    │
                    └─────────────────┘
```

## 🔧 **TECHNICAL STACK**

### **Frontend (React + shadcn/ui)**
- **Framework**: React 18 with CRACO
- **UI Library**: shadcn/ui components
- **Styling**: Tailwind CSS
- **State Management**: React hooks (useState, useEffect)
- **HTTP Client**: Axios
- **Notifications**: Sonner toast notifications

### **Backend Services (FastAPI)**
- **Framework**: FastAPI with Pydantic
- **Database**: MongoDB with Motor (async)
- **Rate Limiting**: SlowAPI
- **Monitoring**: Prometheus metrics
- **CORS**: FastAPI CORS middleware

### **OTP Gateway (FastAPI + Telegram)**
- **Framework**: FastAPI
- **Telegram Integration**: python-telegram-bot
- **Auto-delete**: Scheduled message deletion
- **Rate Limiting**: In-memory rate limiting
- **Security**: Zero persistence (no OTP storage)

### **Infrastructure**
- **Containerization**: Docker + Docker Compose
- **Database**: MongoDB 7.0
- **Reverse Proxy**: Nginx (optional)
- **Health Checks**: Built-in endpoints

## 📁 **FILE STRUCTURE**

```
telega2go/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/ (shadcn/ui components)
│   │   │   └── OTPDashboard.jsx (main dashboard)
│   │   ├── App.js (main app with routing)
│   │   └── index.js
│   ├── Dockerfile (multi-stage build)
│   └── package.json
├── backend/
│   ├── server.py (FastAPI backend)
│   └── requirements.txt
├── otp-social-gateway/
│   ├── app/
│   │   ├── main.py (FastAPI app with CORS)
│   │   ├── otp_service.py (Telegram integration)
│   │   ├── models.py (Pydantic models)
│   │   └── config.py (settings)
│   ├── Dockerfile (multi-stage build)
│   └── requirements.txt
├── docker-compose.yml (orchestration)
└── CHANGELOG.md
```

## 🔌 **API ENDPOINTS**

### **OTP Gateway** (Port 55551)
```
GET  /health          - Health check
GET  /                - Service info
POST /send-otp        - Send OTP via Telegram
POST /webhook         - Telegram webhook (commands, inline queries, callbacks)
GET  /metrics         - Prometheus metrics
```

### **Backend API** (Port 5572)
```
GET  /api/            - Root endpoint
POST /api/status      - Create status check
GET  /api/status      - Get status checks
GET  /docs            - OpenAPI documentation
```

### **Frontend** (Port 5573)
```
GET  /                - OTP Dashboard
GET  /health          - Health monitoring
```

## 🛠️ **KEY IMPLEMENTATIONS**

### **1. CORS Configuration**
```python
# otp-social-gateway/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5573", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **2. Timeout Handling**
```python
# otp-social-gateway/app/main.py
try:
    is_valid = await asyncio.wait_for(otp_service.verify_bot_token(), timeout=10.0)
    if not is_valid:
        logger.warning("Bot token verification failed, but continuing startup")
except asyncio.TimeoutError:
    logger.warning("Bot token verification timed out, but continuing startup")
```

### **3. OTP Dashboard State Management**
```javascript
// frontend/src/components/OTPDashboard.jsx
const [systemStatus, setSystemStatus] = useState({
    otpGateway: 'unknown',
    backend: 'unknown',
    mongodb: 'unknown'
});

const checkSystemHealth = async () => {
    try {
        const otpResponse = await axios.get(`${OTP_GATEWAY_URL}/health`);
        setSystemStatus(prev => ({ ...prev, otpGateway: 'healthy' }));
    } catch (error) {
        setSystemStatus(prev => ({ ...prev, otpGateway: 'error' }));
    }
};
```

### **4. Docker Multi-stage Build**
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
```

## 🔒 **SECURITY FEATURES**

### **OTP Security**
- **Zero Persistence**: OTPs are never stored
- **Auto-delete**: Messages self-destruct after 5-60 seconds
- **Rate Limiting**: 5 OTPs per user per hour
- **Token Validation**: Telegram bot token verification

### **CORS Security**
- **Restricted Origins**: Only allowed frontend domains
- **Credential Support**: Secure cookie handling
- **Method Restrictions**: Controlled HTTP methods

### **Docker Security**
- **Non-root Users**: Services run as non-root
- **Minimal Images**: Alpine Linux base images
- **Health Checks**: Container health monitoring

## 📊 **MONITORING & OBSERVABILITY**

### **Health Checks**
- **Frontend**: Built-in status monitoring
- **Backend**: `/api/` endpoint health
- **OTP Gateway**: `/health` endpoint
- **MongoDB**: Connection status

### **Metrics**
- **Prometheus**: Built-in metrics collection
- **Rate Limiting**: Track rate limit violations
- **OTP Statistics**: Success/failure counts

### **Logging**
- **Structured Logging**: JSON-formatted logs
- **Log Levels**: Configurable (DEBUG, INFO, WARNING, ERROR)
- **Request Tracking**: Full request/response logging

## 🚀 **DEPLOYMENT**

### **Docker Compose**
```bash
# Start all services
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### **Environment Variables**
```bash
# OTP Gateway
TELEGRAM_BOT_TOKEN=your_bot_token_here
DEFAULT_EXPIRE_SECONDS=30
RATE_LIMIT_PER_USER=5

# Backend
MONGO_URL=mongodb://mongodb:27017
DB_NAME=telega2go
CORS_ORIGINS=http://localhost:5573

# Frontend
REACT_APP_BACKEND_URL=http://localhost:5572
REACT_APP_OTP_GATEWAY_URL=http://localhost:5571
```

## 🧪 **TESTING**

### **Manual Testing**
1. **Health Checks**: All services show "healthy"
2. **OTP Sending**: Form validation and API calls
3. **Error Handling**: Proper error messages
4. **CORS**: Cross-origin requests working

### **API Testing**
```bash
# Test OTP Gateway
curl -X POST http://localhost:5571/send-otp \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "123456789", "otp": "123456", "expire_seconds": 30}'

# Test Backend
curl http://localhost:5572/api/

# Test Health
curl http://localhost:5571/health
```

## 📈 **PERFORMANCE**

### **Optimizations**
- **Async/Await**: Non-blocking operations
- **Connection Pooling**: MongoDB connection reuse
- **Docker Caching**: Multi-stage build optimization
- **Health Checks**: Efficient monitoring

### **Scalability**
- **Microservices**: Independent scaling
- **Docker**: Container orchestration
- **MongoDB**: Database scaling support
- **Load Balancing**: Nginx reverse proxy ready

---

**Last Updated**: 2025-10-28  
**Version**: v1.1.0  
**Status**: Production Ready ✅
