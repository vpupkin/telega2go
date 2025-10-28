#!/bin/bash

# 🐳 Telega2Go Docker-Only Management Script
# This script manages ALL operations through Docker containers

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="telega2go"
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"

# Service names
SERVICES=("mongodb" "otp-gateway" "backend" "frontend" "nginx")

# Port mapping
declare -A PORTS=(
    ["frontend"]="5573"
    ["backend"]="5572"
    ["otp-gateway"]="5571"
    ["mongodb"]="5574"
    ["nginx"]="5575"
)

# Functions
print_header() {
    echo -e "${BLUE}🐳 Telega2Go Docker-Only Management${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo
}

print_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  start [service]     Start all services or specific service"
    echo "  stop [service]      Stop all services or specific service"
    echo "  restart [service]   Restart all services or specific service"
    echo "  status              Show status of all services"
    echo "  logs [service]      Show logs for all services or specific service"
    echo "  build [service]     Build all services or specific service"
    echo "  rebuild [service]   Rebuild and start all services or specific service"
    echo "  health              Check health of all services"
    echo "  clean               Clean up stopped containers and unused images"
    echo "  backup              Backup MongoDB data"
    echo "  shell [service]     Open shell in specific service container"
    echo "  url                 Show all service URLs"
    echo "  help                Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start                    # Start all services"
    echo "  $0 start frontend           # Start only frontend"
    echo "  $0 logs backend             # Show backend logs"
    echo "  $0 rebuild otp-gateway      # Rebuild and start OTP gateway"
    echo "  $0 health                   # Check all services health"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is not installed or not in PATH${NC}"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        exit 1
    fi
}

check_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
        cat > "$ENV_FILE" << EOF
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8021082793:AAE56NV3KZ76qkRGrGv9kKk3Wq17n_exvzQ

# OTP Configuration
DEFAULT_EXPIRE_SECONDS=30
RATE_LIMIT_PER_USER=5

# Logging
LOG_LEVEL=INFO

# JWT Secret (Change in production!)
JWT_SECRET=your-super-secret-jwt-key-change-in-production
EOF
        echo -e "${GREEN}✅ Created .env file${NC}"
    fi
}

start_services() {
    local service=$1
    echo -e "${BLUE}🚀 Starting services...${NC}"
    
    if [ -n "$service" ]; then
        echo -e "${YELLOW}Starting $service...${NC}"
        docker-compose up -d "$service"
    else
        echo -e "${YELLOW}Starting all services...${NC}"
        docker-compose up -d
    fi
    
    echo -e "${GREEN}✅ Services started${NC}"
    show_status
}

stop_services() {
    local service=$1
    echo -e "${BLUE}🛑 Stopping services...${NC}"
    
    if [ -n "$service" ]; then
        echo -e "${YELLOW}Stopping $service...${NC}"
        docker-compose stop "$service"
    else
        echo -e "${YELLOW}Stopping all services...${NC}"
        docker-compose down
    fi
    
    echo -e "${GREEN}✅ Services stopped${NC}"
}

restart_services() {
    local service=$1
    echo -e "${BLUE}🔄 Restarting services...${NC}"
    
    if [ -n "$service" ]; then
        echo -e "${YELLOW}Restarting $service...${NC}"
        docker-compose restart "$service"
    else
        echo -e "${YELLOW}Restarting all services...${NC}"
        docker-compose restart
    fi
    
    echo -e "${GREEN}✅ Services restarted${NC}"
    show_status
}

show_status() {
    echo -e "${BLUE}📊 Service Status:${NC}"
    echo
    docker-compose ps
    echo
    show_urls
}

show_logs() {
    local service=$1
    echo -e "${BLUE}📋 Service Logs:${NC}"
    
    if [ -n "$service" ]; then
        echo -e "${YELLOW}Showing logs for $service...${NC}"
        docker-compose logs -f "$service"
    else
        echo -e "${YELLOW}Showing logs for all services...${NC}"
        docker-compose logs -f
    fi
}

build_services() {
    local service=$1
    echo -e "${BLUE}🔨 Building services...${NC}"
    
    if [ -n "$service" ]; then
        echo -e "${YELLOW}Building $service...${NC}"
        docker-compose build "$service"
    else
        echo -e "${YELLOW}Building all services...${NC}"
        docker-compose build
    fi
    
    echo -e "${GREEN}✅ Build completed${NC}"
}

rebuild_services() {
    local service=$1
    echo -e "${BLUE}🔨 Rebuilding services...${NC}"
    
    if [ -n "$service" ]; then
        echo -e "${YELLOW}Rebuilding $service...${NC}"
        docker-compose up -d --build "$service"
    else
        echo -e "${YELLOW}Rebuilding all services...${NC}"
        docker-compose up -d --build
    fi
    
    echo -e "${GREEN}✅ Rebuild completed${NC}"
    show_status
}

check_health() {
    echo -e "${BLUE}🏥 Health Check:${NC}"
    echo
    
    local all_healthy=true
    
    for service in "${SERVICES[@]}"; do
        if [ "$service" = "nginx" ]; then
            continue  # Skip nginx for now
        fi
        
        local port=${PORTS[$service]}
        if [ -n "$port" ]; then
            local url="http://localhost:$port"
            local health_url=""
            
            case $service in
                "frontend")
                    health_url="$url/health"
                    ;;
                "backend")
                    health_url="$url/api/"
                    ;;
                "otp-gateway")
                    health_url="$url/health"
                    ;;
                "mongodb")
                    # MongoDB health check is internal
                    echo -e "${YELLOW}📊 MongoDB: Checking container status...${NC}"
                    if docker-compose ps mongodb | grep -q "Up"; then
                        echo -e "${GREEN}✅ MongoDB: Healthy${NC}"
                    else
                        echo -e "${RED}❌ MongoDB: Unhealthy${NC}"
                        all_healthy=false
                    fi
                    continue
                    ;;
            esac
            
            if [ -n "$health_url" ]; then
                echo -e "${YELLOW}📊 $service: Checking $health_url...${NC}"
                if curl -s -f "$health_url" > /dev/null 2>&1; then
                    echo -e "${GREEN}✅ $service: Healthy${NC}"
                else
                    echo -e "${RED}❌ $service: Unhealthy${NC}"
                    all_healthy=false
                fi
            fi
        fi
    done
    
    echo
    if [ "$all_healthy" = true ]; then
        echo -e "${GREEN}🎉 All services are healthy!${NC}"
    else
        echo -e "${RED}⚠️  Some services are unhealthy. Check logs for details.${NC}"
    fi
}

clean_up() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    
    echo -e "${YELLOW}Removing stopped containers...${NC}"
    docker-compose rm -f
    
    echo -e "${YELLOW}Removing unused images...${NC}"
    docker image prune -f
    
    echo -e "${YELLOW}Removing unused volumes...${NC}"
    docker volume prune -f
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

backup_data() {
    echo -e "${BLUE}💾 Creating backup...${NC}"
    
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    echo -e "${YELLOW}Backing up MongoDB...${NC}"
    docker-compose exec -T mongodb mongodump --out /backup
    docker cp "$(docker-compose ps -q mongodb):/backup" "$backup_dir/mongodb"
    
    echo -e "${GREEN}✅ Backup created in $backup_dir${NC}"
}

open_shell() {
    local service=$1
    
    if [ -z "$service" ]; then
        echo -e "${RED}❌ Please specify a service name${NC}"
        echo "Available services: ${SERVICES[*]}"
        exit 1
    fi
    
    echo -e "${BLUE}🐚 Opening shell in $service...${NC}"
    docker-compose exec "$service" /bin/sh
}

show_urls() {
    echo -e "${BLUE}🌐 Service URLs:${NC}"
    echo
    echo -e "${GREEN}📱 Frontend PWA:${NC}     http://localhost:5573"
    echo -e "${GREEN}🔧 Backend API:${NC}      http://localhost:5572"
    echo -e "${GREEN}📨 OTP Gateway:${NC}      http://localhost:5571"
    echo -e "${GREEN}🗄️  MongoDB:${NC}         localhost:5574"
    echo -e "${GREEN}🌐 Nginx Proxy:${NC}      http://localhost:5575"
    echo
    echo -e "${YELLOW}📋 API Documentation:${NC}"
    echo -e "   Backend: http://localhost:5572/docs"
    echo -e "   OTP Gateway: http://localhost:5571/docs"
    echo
}

# Main script logic
main() {
    print_header
    check_docker
    check_env_file
    
    case "${1:-help}" in
        "start")
            start_services "$2"
            ;;
        "stop")
            stop_services "$2"
            ;;
        "restart")
            restart_services "$2"
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "build")
            build_services "$2"
            ;;
        "rebuild")
            rebuild_services "$2"
            ;;
        "health")
            check_health
            ;;
        "clean")
            clean_up
            ;;
        "backup")
            backup_data
            ;;
        "shell")
            open_shell "$2"
            ;;
        "url")
            show_urls
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

# Run main function with all arguments
main "$@"
