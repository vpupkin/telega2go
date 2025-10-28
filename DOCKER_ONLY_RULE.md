# 🐳 DOCKER-ONLY RULE - PROJECT POLICY

## 🚨 CRITICAL PROJECT RULE

**ALL PROJECT OPERATIONS MUST USE DOCKER EXCLUSIVELY**

### ❌ FORBIDDEN ACTIONS
- ❌ Running services directly with Python/Node.js
- ❌ Using local virtual environments
- ❌ Installing dependencies locally
- ❌ Running `npm start`, `uvicorn`, `python` directly
- ❌ Using local MongoDB instances
- ❌ Any non-Docker service management

### ✅ REQUIRED ACTIONS
- ✅ Use `docker-compose` for all operations
- ✅ All services run in containers
- ✅ Use Docker health checks
- ✅ Use Docker networking
- ✅ Use Docker volumes for persistence

## 🎯 DOCKER-ONLY COMMANDS

### Start All Services
```bash
docker-compose up --build -d
```

### Stop All Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Restart Services
```bash
docker-compose restart
```

### Check Status
```bash
docker-compose ps
```

## 🔧 DOCKER-ONLY TROUBLESHOOTING

### If Docker Compose Fails
```bash
# Check Docker daemon
sudo systemctl status docker

# Start Docker if needed
sudo systemctl start docker

# Check Docker Compose
docker-compose --version
```

### If Services Don't Start
```bash
# Rebuild everything
docker-compose down
docker-compose up --build -d

# Check logs
docker-compose logs [service-name]
```

### If Ports Are Busy
```bash
# Check what's using ports
sudo netstat -tulpn | grep :557

# Kill conflicting processes
sudo pkill -f "port 557"
```

## 📋 DOCKER-ONLY SERVICE MANAGEMENT

| Operation | Docker Command |
|-----------|----------------|
| Start all | `docker-compose up -d` |
| Stop all | `docker-compose down` |
| Restart | `docker-compose restart` |
| Logs | `docker-compose logs -f` |
| Status | `docker-compose ps` |
| Rebuild | `docker-compose up --build -d` |
| Clean | `docker-compose down -v --rmi all` |

## 🚀 DOCKER-ONLY STARTUP SCRIPT

The project includes `docker-start.sh` which handles all Docker operations:

```bash
./docker-start.sh start    # Start all services
./docker-start.sh stop     # Stop all services
./docker-start.sh restart  # Restart all services
./docker-start.sh logs     # View logs
./docker-start.sh status   # Check status
```

## ⚠️ ENFORCEMENT

**This rule is MANDATORY and will be enforced:**
- All future operations MUST use Docker
- No exceptions for "quick testing"
- No local development without Docker
- All documentation assumes Docker usage

---

**REMEMBER: DOCKER ONLY - NO EXCEPTIONS! 🐳**
