# 🐳 DOCKER-ONLY DEPLOYMENT GUIDE

## 🎯 **PROJECT RULE: DOCKER-ONLY OPERATIONS**

This project operates **EXCLUSIVELY** using Docker containers. All services, development, testing, and deployment must be done through Docker.

---

## 🚀 **QUICK START (DOCKER-ONLY)**

### **1. Start All Services**
```bash
# Start all services with Docker Compose
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### **2. Access the Application**
- **Frontend PWA**: http://localhost:5573
- **Backend API**: http://localhost:5572
- **OTP Gateway**: http://localhost:5571
- **MongoDB**: localhost:5574

---

## 📋 **SERVICE ARCHITECTURE**

### **Port Mapping (557 Prefix)**
| Service | Internal Port | External Port | Purpose |
|---------|---------------|---------------|---------|
| Frontend | 80 | 5573 | PWA User Registration |
| Backend | 8000 | 5572 | REST API |
| OTP Gateway | 55155 | 5571 | Telegram OTP Service |
| MongoDB | 27017 | 5574 | Database |
| Nginx | 80/443 | 5575/5576 | Reverse Proxy (Optional) |

### **Service Dependencies**
```
MongoDB (5574)
    ↓
OTP Gateway (5571) ← Backend (5572)
    ↓                    ↓
Frontend (5573) ←────────┘
```

---

## 🛠️ **DOCKER COMMANDS**

### **Basic Operations**
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View logs
docker-compose logs -f [service-name]

# Check status
docker-compose ps
```

### **Individual Service Management**
```bash
# Start specific service
docker-compose up -d [service-name]

# Stop specific service
docker-compose stop [service-name]

# Restart specific service
docker-compose restart [service-name]

# Rebuild and start service
docker-compose up -d --build [service-name]
```

### **Development Commands**
```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build [service-name]

# View service logs
docker-compose logs -f [service-name]

# Execute command in running container
docker-compose exec [service-name] [command]
```

---

## 🔧 **ENVIRONMENT CONFIGURATION**

### **Required Environment Variables**
```bash
# Telegram Bot Token (REQUIRED)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional Configuration
DEFAULT_EXPIRE_SECONDS=30
RATE_LIMIT_PER_USER=5
LOG_LEVEL=INFO
JWT_SECRET=your-super-secret-jwt-key-change-in-production
```

### **Environment File (.env)**
Create a `.env` file in the project root:
```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8021082793:AAE56NV3KZ76qkRGrGv9kKk3Wq17n_exvzQ

# OTP Configuration
DEFAULT_EXPIRE_SECONDS=30
RATE_LIMIT_PER_USER=5

# Logging
LOG_LEVEL=INFO

# JWT Secret (Change in production!)
JWT_SECRET=your-super-secret-jwt-key-change-in-production
```

---

## 🏗️ **DOCKERFILE STRUCTURE**

### **Frontend Dockerfile**
```dockerfile
# Multi-stage build for React PWA
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### **Backend Dockerfile**
```dockerfile
FROM python:3.10-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **OTP Gateway Dockerfile**
```dockerfile
FROM python:3.10-slim-buster
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 55155
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "55155"]
```

---

## 🔍 **HEALTH CHECKS**

### **Service Health Endpoints**
- **Frontend**: http://localhost:5573/health
- **Backend**: http://localhost:5572/api/
- **OTP Gateway**: http://localhost:5571/health
- **MongoDB**: Internal health check

### **Health Check Commands**
```bash
# Check all services
docker-compose ps

# Check specific service health
curl http://localhost:5573/health
curl http://localhost:5572/api/
curl http://localhost:5571/health

# View health check logs
docker-compose logs [service-name] | grep health
```

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues**

#### **1. Port Already in Use**
```bash
# Check what's using the port
sudo netstat -tulpn | grep :5573

# Stop conflicting services
docker-compose down
```

#### **2. Container Won't Start**
```bash
# Check container logs
docker-compose logs [service-name]

# Check container status
docker-compose ps -a
```

#### **3. Service Communication Issues**
```bash
# Check network connectivity
docker-compose exec frontend ping backend
docker-compose exec backend ping otp-gateway

# Check service URLs
docker-compose exec frontend curl http://backend:8000/api/
```

#### **4. Database Connection Issues**
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Test MongoDB connection
docker-compose exec backend python -c "import motor; print('MongoDB OK')"
```

---

## 📊 **MONITORING & LOGS**

### **View All Logs**
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f [service-name]

# Last 100 lines
docker-compose logs --tail=100 [service-name]
```

### **Resource Usage**
```bash
# Container resource usage
docker stats

# Specific container
docker stats telega2go-frontend
```

---

## 🔄 **DEVELOPMENT WORKFLOW**

### **1. Code Changes**
```bash
# After making changes, rebuild and restart
docker-compose up -d --build [service-name]

# Or rebuild all
docker-compose up -d --build
```

### **2. Database Changes**
```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh

# Backup database
docker-compose exec mongodb mongodump --out /backup
```

### **3. Testing**
```bash
# Run tests in container
docker-compose exec backend python -m pytest
docker-compose exec otp-gateway python -m pytest
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

### **2. Start Production Services**
```bash
# Start with production profile
docker-compose --profile production up -d

# Or start specific services
docker-compose up -d mongodb otp-gateway backend frontend
```

### **3. SSL/HTTPS Setup**
```bash
# Start with Nginx reverse proxy
docker-compose --profile production up -d nginx
```

---

## 📝 **MAINTENANCE**

### **Cleanup Commands**
```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Full cleanup (careful!)
docker system prune -a
```

### **Backup Commands**
```bash
# Backup MongoDB
docker-compose exec mongodb mongodump --out /backup

# Backup volumes
docker run --rm -v telega2go_mongodb_data:/data -v $(pwd):/backup alpine tar czf /backup/mongodb-backup.tar.gz -C /data .
```

---

## ⚠️ **IMPORTANT RULES**

1. **NEVER** run services outside Docker
2. **ALWAYS** use Docker Compose for orchestration
3. **ALWAYS** use the 557 port prefix
4. **NEVER** install dependencies locally
5. **ALWAYS** rebuild containers after code changes
6. **ALWAYS** check health endpoints after deployment

---

## 🎯 **SUCCESS CRITERIA**

✅ All services running in Docker containers  
✅ All services accessible on 557 ports  
✅ Health checks passing  
✅ Services communicating properly  
✅ No local dependencies required  
✅ Single command deployment (`docker-compose up -d`)

---

**🐳 DOCKER-ONLY: The only way to deploy Telega2Go! 🐳**
