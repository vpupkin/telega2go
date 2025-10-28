#!/bin/bash

# 🐳 Telega2Go Simple Docker-Only Management
# Works around Docker Compose issues by using direct Docker commands

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Container names
FRONTEND="telega2go-frontend"
BACKEND="telega2go-backend"
OTP_GATEWAY="telega2go-otp-gateway"
MONGODB="telega2go-mongodb"

# Ports
FRONTEND_PORT="5573"
BACKEND_PORT="5572"
OTP_PORT="5571"
MONGO_PORT="5574"

print_header() {
    echo -e "${BLUE}🐳 Telega2Go Docker-Only Management${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo
}

print_usage() {
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start     Start all services"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  status    Show status of all services"
    echo "  logs      Show logs for all services"
    echo "  health    Check health of all services"
    echo "  url       Show all service URLs"
    echo "  clean     Clean up stopped containers"
    echo "  help      Show this help"
    echo
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi
}

start_services() {
    echo -e "${BLUE}🚀 Starting Telega2Go services...${NC}"
    
    # Start MongoDB
    echo -e "${YELLOW}Starting MongoDB...${NC}"
    docker run -d --name $MONGODB \
        -p $MONGO_PORT:27017 \
        -e MONGO_INITDB_ROOT_USERNAME=admin \
        -e MONGO_INITDB_ROOT_PASSWORD=password123 \
        -e MONGO_INITDB_DATABASE=telega2go \
        mongo:7.0 || echo "MongoDB already running"
    
    # Start OTP Gateway
    echo -e "${YELLOW}Starting OTP Gateway...${NC}"
    docker run -d --name $OTP_GATEWAY \
        -p $OTP_PORT:55155 \
        -e TELEGRAM_BOT_TOKEN=8021082793:AAE56NV3KZ76qkRGrGv9kKk3Wq17n_exvzQ \
        -e DEFAULT_EXPIRE_SECONDS=30 \
        -e RATE_LIMIT_PER_USER=5 \
        -e PORT=55155 \
        -e LOG_LEVEL=INFO \
        --link $MONGODB:mongodb \
        telega2go-otp-gateway || echo "OTP Gateway already running"
    
    # Start Backend
    echo -e "${YELLOW}Starting Backend...${NC}"
    docker run -d --name $BACKEND \
        -p $BACKEND_PORT:8000 \
        -e MONGO_URL=mongodb://admin:password123@mongodb:27017/telega2go?authSource=admin \
        -e DB_NAME=telega2go \
        -e CORS_ORIGINS=http://localhost:5573,http://localhost:80 \
        -e JWT_SECRET=your-super-secret-jwt-key-change-in-production \
        -e OTP_GATEWAY_URL=http://otp-gateway:55155 \
        --link $MONGODB:mongodb \
        --link $OTP_GATEWAY:otp-gateway \
        telega2go-backend || echo "Backend already running"
    
    # Start Frontend
    echo -e "${YELLOW}Starting Frontend...${NC}"
    docker run -d --name $FRONTEND \
        -p $FRONTEND_PORT:80 \
        -e REACT_APP_BACKEND_URL=http://localhost:5572 \
        -e REACT_APP_OTP_GATEWAY_URL=http://localhost:5571 \
        telega2go-frontend || echo "Frontend already running"
    
    echo -e "${GREEN}✅ All services started!${NC}"
    show_status
}

stop_services() {
    echo -e "${BLUE}🛑 Stopping Telega2Go services...${NC}"
    
    docker stop $FRONTEND $BACKEND $OTP_GATEWAY $MONGODB 2>/dev/null || true
    docker rm $FRONTEND $BACKEND $OTP_GATEWAY $MONGODB 2>/dev/null || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
}

restart_services() {
    echo -e "${BLUE}🔄 Restarting Telega2Go services...${NC}"
    stop_services
    sleep 2
    start_services
}

show_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    echo
    docker ps --filter "name=telega2go" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo
    show_urls
}

show_logs() {
    echo -e "${BLUE}📋 Service Logs:${NC}"
    echo
    for service in $FRONTEND $BACKEND $OTP_GATEWAY $MONGODB; do
        if docker ps --format "{{.Names}}" | grep -q "^$service$"; then
            echo -e "${YELLOW}=== $service ===${NC}"
            docker logs --tail=10 $service
            echo
        fi
    done
}

check_health() {
    echo -e "${BLUE}🏥 Health Check:${NC}"
    echo
    
    # Check Frontend
    if curl -s -f http://localhost:$FRONTEND_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend: Healthy${NC}"
    else
        echo -e "${RED}❌ Frontend: Unhealthy${NC}"
    fi
    
    # Check Backend
    if curl -s -f http://localhost:$BACKEND_PORT/api/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend: Healthy${NC}"
    else
        echo -e "${RED}❌ Backend: Unhealthy${NC}"
    fi
    
    # Check OTP Gateway
    if curl -s -f http://localhost:$OTP_PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OTP Gateway: Healthy${NC}"
    else
        echo -e "${RED}❌ OTP Gateway: Unhealthy${NC}"
    fi
    
    # Check MongoDB
    if docker ps --format "{{.Names}}" | grep -q "^$MONGODB$"; then
        echo -e "${GREEN}✅ MongoDB: Running${NC}"
    else
        echo -e "${RED}❌ MongoDB: Not Running${NC}"
    fi
}

show_urls() {
    echo -e "${BLUE}🌐 Service URLs:${NC}"
    echo
    echo -e "${GREEN}📱 Frontend PWA:${NC}     http://localhost:$FRONTEND_PORT"
    echo -e "${GREEN}🔧 Backend API:${NC}      http://localhost:$BACKEND_PORT"
    echo -e "${GREEN}📨 OTP Gateway:${NC}      http://localhost:$OTP_PORT"
    echo -e "${GREEN}🗄️  MongoDB:${NC}         localhost:$MONGO_PORT"
    echo
    echo -e "${YELLOW}📋 API Documentation:${NC}"
    echo -e "   Backend: http://localhost:$BACKEND_PORT/docs"
    echo -e "   OTP Gateway: http://localhost:$OTP_PORT/docs"
    echo
}

clean_up() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    
    # Stop and remove containers
    docker stop $FRONTEND $BACKEND $OTP_GATEWAY $MONGODB 2>/dev/null || true
    docker rm $FRONTEND $BACKEND $OTP_GATEWAY $MONGODB 2>/dev/null || true
    
    # Remove unused images
    docker image prune -f
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main script logic
main() {
    print_header
    check_docker
    
    case "${1:-help}" in
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "health")
            check_health
            ;;
        "url")
            show_urls
            ;;
        "clean")
            clean_up
            ;;
        "help"|"-h"|"--help")
            print_usage
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $1${NC}"
            echo
            print_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
