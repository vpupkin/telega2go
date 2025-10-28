# 🐳 Telega2Go Docker Setup

This document provides a comprehensive guide for running the Telega2Go project using Docker Compose, avoiding any local system changes.

## 🎯 Project Overview

Telega2Go is a complete OTP delivery platform with:
- **OTP Social Gateway**: Sends OTPs via Telegram with self-destructing messages
- **Backend API**: FastAPI service with MongoDB integration
- **Frontend**: React application with modern UI components
- **MongoDB**: Database for status tracking and data persistence

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Telegram Bot Token (get from @BotFather)

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd telega2go
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your Telegram bot token
nano .env
```

**Required Environment Variables:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 3. Start All Services

```bash
# Option 1: Use the startup script (recommended)
./start.sh

# Option 2: Manual Docker Compose
docker-compose up --build -d
```

### 4. Verify Services

The startup script will check all services, or you can verify manually:

```bash
# Check all services
docker-compose ps

# Check individual services
curl http://localhost:3000      # Frontend
curl http://localhost:8000/api/ # Backend
curl http://localhost:55155/health # OTP Gateway
```

## 📋 Service Details

### Services and Ports

| Service | Port | Description | Health Check |
|---------|------|-------------|--------------|
| Frontend | 5573 | React application | http://localhost:5573 |
| Backend | 5572 | FastAPI service | http://localhost:5572/api/ |
| OTP Gateway | 5571 | Telegram OTP service | http://localhost:5571/health |
| MongoDB | 5574 | Database | Internal health check |

### API Endpoints

#### Backend API (http://localhost:5572)
- `GET /api/` - Hello World
- `POST /api/status` - Create status check
- `GET /api/status` - Get status checks
- `GET /docs` - OpenAPI documentation

#### OTP Gateway (http://localhost:5571)
- `POST /send-otp` - Send OTP via Telegram
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics
- `GET /docs` - OpenAPI documentation

## 🔧 Management Commands

### Basic Operations

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f frontend
docker-compose logs -f backend
docker-compose logs -f otp-gateway
docker-compose logs -f mongodb
```

### Development Commands

```bash
# Rebuild and start
docker-compose up --build -d

# Start with logs
docker-compose up --build

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec otp-gateway bash
```

### Database Operations

```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh

# Backup database
docker-compose exec mongodb mongodump --out /backup

# Restore database
docker-compose exec mongodb mongorestore /backup
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Telegram Bot Configuration (REQUIRED)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# OTP Gateway Configuration
DEFAULT_EXPIRE_SECONDS=30
RATE_LIMIT_PER_USER=5
LOG_LEVEL=INFO

# Database Configuration
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=password123
MONGO_INITDB_DATABASE=telega2go

# CORS Configuration
CORS_ORIGINS=http://localhost:5573,http://localhost:80
```

### Service Configuration

#### Frontend Configuration
- **Build**: React with shadcn/ui components
- **Port**: 3000 (mapped to 80 in container)
- **Proxy**: API calls proxied to backend

#### Backend Configuration
- **Framework**: FastAPI with async support
- **Database**: MongoDB with Motor driver
- **Port**: 8000
- **CORS**: Configured for frontend

#### OTP Gateway Configuration
- **Framework**: FastAPI with Telegram Bot API
- **Port**: 55155
- **Features**: Self-destructing messages, rate limiting

## 🔍 Troubleshooting

### Common Issues

#### 1. OTP Gateway Not Starting
```bash
# Check logs
docker-compose logs otp-gateway

# Common causes:
# - Invalid TELEGRAM_BOT_TOKEN
# - Network connectivity issues
```

#### 2. Frontend Build Failures
```bash
# Rebuild frontend
docker-compose build --no-cache frontend

# Check for dependency issues
docker-compose exec frontend npm install --legacy-peer-deps
```

#### 3. Backend Database Connection Issues
```bash
# Check MongoDB status
docker-compose logs mongodb

# Verify connection string
docker-compose exec backend python -c "import os; print(os.environ['MONGO_URL'])"
```

#### 4. Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
netstat -tulpn | grep :55155

# Stop conflicting services or change ports in docker-compose.yml
```

### Health Checks

```bash
# Check all service health
docker-compose ps

# Individual health checks
curl http://localhost:3000/health
curl http://localhost:8000/api/
curl http://localhost:55155/health
```

### Logs Analysis

```bash
# View all logs
docker-compose logs

# Filter by service
docker-compose logs frontend | grep ERROR
docker-compose logs backend | grep ERROR
docker-compose logs otp-gateway | grep ERROR
```

## 🚀 Production Deployment

### Using Nginx Reverse Proxy

The project includes an optional Nginx reverse proxy for production:

```bash
# Start with Nginx
docker-compose --profile production up -d

# This will start:
# - All services
# - Nginx reverse proxy on port 80
```

### Environment-Specific Configuration

For production, update the `.env` file:

```env
# Production settings
NODE_ENV=production
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
```

### Security Considerations

1. **Change default passwords** in production
2. **Use HTTPS** with proper SSL certificates
3. **Restrict CORS origins** to your domain
4. **Use secrets management** for sensitive data
5. **Enable firewall rules** for database access

## 📊 Monitoring

### Built-in Monitoring

- **Health Checks**: All services have health check endpoints
- **Prometheus Metrics**: OTP Gateway exposes metrics
- **Structured Logging**: JSON logs with timestamps

### External Monitoring

```bash
# Prometheus metrics
curl http://localhost:55155/metrics

# Service status
curl http://localhost:8000/api/status
```

## 🔄 Updates and Maintenance

### Updating Services

```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up --build -d
```

### Data Persistence

- **MongoDB data**: Stored in `mongodb_data` volume
- **Backup**: Use `mongodump` for database backups
- **Restore**: Use `mongorestore` for database restoration

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/)
- [MongoDB Documentation](https://docs.mongodb.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure Docker and Docker Compose are running
4. Check port availability
5. Verify Telegram bot token is valid

---

**Happy coding! 🚀**
