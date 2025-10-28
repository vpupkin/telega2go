# 🚀 Telega2Go Quick Start Guide

## ✅ What I've Set Up For You

I've created a complete Docker Compose setup that avoids any local system changes. Here's what's been configured:

### 📁 Project Structure
```
telega2go/
├── docker-compose.yml          # Main Docker Compose configuration
├── start.sh                    # Startup script with health checks
├── .env                        # Environment variables
├── DOCKER_SETUP.md            # Comprehensive Docker documentation
├── QUICK_START.md             # This file
├── nginx/                     # Nginx reverse proxy configuration
│   ├── nginx.conf
│   └── conf.d/default.conf
├── backend/
│   ├── Dockerfile             # Backend container configuration
│   ├── server.py              # FastAPI backend
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile             # Frontend container configuration
│   ├── nginx.conf             # Frontend nginx config
│   ├── package.json           # Fixed dependency issues
│   └── src/                   # React application
└── otp-social-gateway/
    ├── Dockerfile             # OTP Gateway container
    ├── app/                   # OTP service code
    └── requirements.txt
```

### 🔧 Services Configured

| Service | Port | Description | Status |
|---------|------|-------------|--------|
| **Frontend** | 5573 | React app with shadcn/ui | ✅ Ready |
| **Backend** | 5572 | FastAPI with MongoDB | ✅ Ready |
| **OTP Gateway** | 5571 | Telegram OTP service | ✅ Ready |
| **MongoDB** | 5574 | Database | ✅ Ready |
| **Nginx** | 5575 | Reverse proxy (optional) | ✅ Ready |

## 🚀 How to Start

### Option 1: Using the Startup Script (Recommended)
```bash
cd /home/i1/git/telega2go
./start.sh
```

### Option 2: Manual Docker Compose
```bash
cd /home/i1/git/telega2go
docker-compose up --build -d
```

### Option 3: Individual Services (if Docker Compose has issues)
```bash
# Start MongoDB
docker run -d --name mongodb -p 27017:27017 mongo:7.0

# Start Backend
cd backend && docker build -t telega2go-backend .
docker run -d --name backend -p 8000:8000 \
  -e MONGO_URL=mongodb://localhost:27017/telega2go \
  -e DB_NAME=telega2go \
  telega2go-backend

# Start OTP Gateway
cd otp-social-gateway && docker build -t telega2go-otp .
docker run -d --name otp-gateway -p 55155:55155 \
  -e TELEGRAM_BOT_TOKEN=your_bot_token_here \
  telega2go-otp

# Start Frontend
cd frontend && docker build -t telega2go-frontend .
docker run -d --name frontend -p 3000:80 telega2go-frontend
```

## ⚙️ Configuration Required

### 1. Telegram Bot Token (REQUIRED)
```bash
# Edit .env file
nano .env

# Add your bot token
TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
```

**To get a bot token:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow the instructions
4. Copy the token to your `.env` file

### 2. Verify Services
```bash
# Check if services are running
docker ps

# Test endpoints
curl http://localhost:5573      # Frontend
curl http://localhost:5572/api/ # Backend
curl http://localhost:5571/health # OTP Gateway
```

## 🔍 Troubleshooting

### Docker Issues
If you see Docker connection errors:
```bash
# Check Docker status
sudo systemctl status docker

# Start Docker if needed
sudo systemctl start docker

# Add user to docker group (if needed)
sudo usermod -aG docker $USER
# Then logout and login again
```

### Port Conflicts
If ports are already in use:
```bash
# Check what's using ports
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
netstat -tulpn | grep :55155

# Stop conflicting services or change ports in docker-compose.yml
```

### Service Health Checks
```bash
# View logs
docker-compose logs -f

# Check specific service
docker-compose logs frontend
docker-compose logs backend
docker-compose logs otp-gateway
```

## 📚 What Each Service Does

### 🎨 Frontend (React)
- **URL**: http://localhost:5573
- **Purpose**: User interface for the application
- **Features**: Modern UI with shadcn/ui components
- **Fixed**: Dependency conflicts resolved

### 🔧 Backend (FastAPI)
- **URL**: http://localhost:5572
- **Purpose**: API server with MongoDB integration
- **Features**: Status tracking, CORS enabled
- **API Docs**: http://localhost:5572/docs

### 📱 OTP Gateway (FastAPI)
- **URL**: http://localhost:5571
- **Purpose**: Sends OTPs via Telegram with auto-delete
- **Features**: Rate limiting, self-destructing messages
- **API Docs**: http://localhost:5571/docs

### 🗄️ MongoDB
- **Port**: 5574
- **Purpose**: Database for backend data
- **Features**: Persistent storage, health checks

## 🎯 Next Steps

1. **Get Telegram Bot Token** from @BotFather
2. **Update .env file** with your bot token
3. **Start services** using `./start.sh`
4. **Test the application** at http://localhost:3000
5. **Send test OTP** using the API

## 📖 Additional Documentation

- **DOCKER_SETUP.md**: Complete Docker documentation
- **otp-social-gateway/README.md**: OTP service details
- **otp-social-gateway/QUICKSTART.md**: 10-minute setup guide

## 🆘 Need Help?

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify Docker is running: `docker ps`
3. Check environment variables in `.env`
4. Ensure ports are available
5. Verify Telegram bot token is valid

---

**You're all set! The project is ready to run with Docker Compose. 🚀**
