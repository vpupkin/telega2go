# 🐳 Telega2Go - PWA User Registration System

## ⚠️ **DOCKER-ONLY PROJECT** ⚠️

This project operates **EXCLUSIVELY** using Docker containers. All development, testing, and deployment must be done through Docker.

---

## 🚀 **QUICK START (DOCKER-ONLY)**

### **1. Prerequisites**
- Docker (20.10+)
- Docker Compose (2.0+)
- Git

### **2. Clone and Start**
```bash
# Clone the repository
git clone <repository-url>
cd telega2go

# Start all services (DOCKER-ONLY)
./docker-manage.sh start

# Or using docker-compose directly
docker-compose up -d
```

### **3. Access the Application**
- **🌐 Frontend PWA**: http://localhost:5573
- **🔧 Backend API**: http://localhost:5572
- **📨 OTP Gateway**: http://localhost:5571
- **🗄️ MongoDB**: localhost:5574

---

## 🎯 **PROJECT OVERVIEW**

Telega2Go is a **PWA User Registration System** that provides easy user registration for web applications using Telegram OTP verification.

### **Key Features**
- ✅ **PWA Support** - Installable, offline-capable
- ✅ **Telegram OTP** - Secure verification via Telegram Bot
- ✅ **JWT Authentication** - Secure user sessions
- ✅ **Docker-Only** - No local dependencies required
- ✅ **Modern UI** - Built with React and shadcn/ui
- ✅ **Self-destructing Messages** - OTPs auto-delete after 30 seconds

---

## 🏗️ **ARCHITECTURE**

### **Services (All Dockerized)**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend PWA  │    │   Backend API   │    │  OTP Gateway    │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
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

### **Port Configuration (557 Prefix)**
| Service | Internal | External | Purpose |
|---------|----------|----------|---------|
| Frontend | 80 | 5573 | PWA Interface |
| Backend | 8000 | 5572 | REST API |
| OTP Gateway | 55155 | 5571 | Telegram OTP |
| MongoDB | 27017 | 5574 | Database |

---

## 🛠️ **DOCKER MANAGEMENT**

### **Using the Management Script**
```bash
# Start all services
./docker-manage.sh start

# Start specific service
./docker-manage.sh start frontend

# Check status
./docker-manage.sh status

# View logs
./docker-manage.sh logs

# Health check
./docker-manage.sh health

# Rebuild services
./docker-manage.sh rebuild

# Stop all services
./docker-manage.sh stop

# Clean up
./docker-manage.sh clean
```

### **Using Docker Compose Directly**
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d frontend

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild and start
docker-compose up -d --build
```

---

## 🔧 **CONFIGURATION**

### **Environment Variables**
Create a `.env` file in the project root:
```bash
# Telegram Bot Token (REQUIRED)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional Configuration
DEFAULT_EXPIRE_SECONDS=30
RATE_LIMIT_PER_USER=5
LOG_LEVEL=INFO
JWT_SECRET=your-super-secret-jwt-key-change-in-production
```

### **Telegram Bot Setup**
1. Create a bot with [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Add the token to `.env` file
4. Start a conversation with your bot
5. Get your Chat ID from [@userinfobot](https://t.me/userinfobot)

---

## 📱 **USER REGISTRATION FLOW**

### **Step 1: Registration Form**
- User enters: Name, Email, Phone, Telegram Chat ID
- System validates input and creates registration session

### **Step 2: OTP Verification**
- System sends 6-digit OTP to user's Telegram
- OTP auto-deletes after 30 seconds
- User enters OTP to verify account

### **Step 3: Account Creation**
- System creates user account with JWT token
- User is logged in and ready to use the system

---

## 🔍 **API ENDPOINTS**

### **Backend API (Port 5572)**
```
POST /api/register          # Start registration
POST /api/verify-otp        # Verify OTP
POST /api/resend-otp        # Resend OTP
GET  /api/profile           # Get user profile
GET  /api/                  # Health check
GET  /docs                  # API documentation
```

### **OTP Gateway (Port 5571)**
```
POST /send-otp              # Send OTP via Telegram
GET  /health                # Health check
GET  /docs                  # API documentation
```

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

#### **1. Services Won't Start**
```bash
# Check Docker status
docker --version
docker-compose --version

# Check service logs
./docker-manage.sh logs

# Rebuild services
./docker-manage.sh rebuild
```

#### **2. Port Conflicts**
```bash
# Check what's using ports
sudo netstat -tulpn | grep :5573

# Stop conflicting services
docker-compose down
```

#### **3. Database Issues**
```bash
# Check MongoDB logs
./docker-manage.sh logs mongodb

# Restart MongoDB
./docker-manage.sh restart mongodb
```

#### **4. OTP Not Sending**
- Verify Telegram Bot Token is correct
- Ensure user has started conversation with bot
- Check Chat ID is correct (use @userinfobot)

---

## 📊 **MONITORING**

### **Health Checks**
```bash
# Check all services
./docker-manage.sh health

# Individual service checks
curl http://localhost:5573/health    # Frontend
curl http://localhost:5572/api/      # Backend
curl http://localhost:5571/health    # OTP Gateway
```

### **Logs**
```bash
# All services
./docker-manage.sh logs

# Specific service
./docker-manage.sh logs frontend
./docker-manage.sh logs backend
./docker-manage.sh logs otp-gateway
```

---

## 🔄 **DEVELOPMENT**

### **Making Changes**
1. Edit code in your preferred editor
2. Rebuild the affected service:
   ```bash
   ./docker-manage.sh rebuild frontend
   ```
3. Check logs for any issues:
   ```bash
   ./docker-manage.sh logs frontend
   ```

### **Adding New Dependencies**
1. Update `package.json` (frontend) or `requirements.txt` (backend/otp-gateway)
2. Rebuild the service:
   ```bash
   ./docker-manage.sh rebuild [service-name]
   ```

---

## 🚀 **PRODUCTION DEPLOYMENT**

### **1. Environment Setup**
```bash
# Copy production environment
cp .env.example .env.production

# Edit production settings
nano .env.production
```

### **2. Deploy**
```bash
# Start production services
docker-compose --profile production up -d

# Or start specific services
docker-compose up -d mongodb otp-gateway backend frontend
```

### **3. SSL/HTTPS (Optional)**
```bash
# Start with Nginx reverse proxy
docker-compose --profile production up -d nginx
```

---

## 📝 **MAINTENANCE**

### **Backup**
```bash
# Create backup
./docker-manage.sh backup

# Manual MongoDB backup
docker-compose exec mongodb mongodump --out /backup
```

### **Cleanup**
```bash
# Clean up unused resources
./docker-manage.sh clean

# Remove all containers and volumes (careful!)
docker-compose down -v
docker system prune -a
```

---

## ⚠️ **IMPORTANT RULES**

1. **🐳 DOCKER-ONLY**: Never run services outside Docker
2. **🔌 PORT PREFIX**: Always use 557 prefix for external ports
3. **📦 NO LOCAL DEPS**: Never install dependencies locally
4. **🔄 REBUILD**: Always rebuild after code changes
5. **🏥 HEALTH CHECKS**: Always verify services are healthy
6. **📋 LOGS**: Check logs when troubleshooting

---

## 🎯 **SUCCESS CRITERIA**

✅ All services running in Docker containers  
✅ All services accessible on 557 ports  
✅ Health checks passing  
✅ Services communicating properly  
✅ No local dependencies required  
✅ Single command deployment (`./docker-manage.sh start`)

---

## 📚 **DOCUMENTATION**

- [DOCKER_ONLY_SETUP.md](DOCKER_ONLY_SETUP.md) - Detailed Docker setup guide
- [docker-manage.sh](docker-manage.sh) - Management script
- [docker-compose.yml](docker-compose.yml) - Service orchestration
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

## 🤝 **CONTRIBUTING**

1. Fork the repository
2. Create a feature branch
3. Make changes (Docker-only!)
4. Test with `./docker-manage.sh health`
5. Submit a pull request

---

**🐳 Remember: DOCKER-ONLY is not just a rule, it's the way! 🐳**
