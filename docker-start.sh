#!/bin/bash

# Telega2Go Docker-Only Startup Script
# This script handles ALL project operations using Docker exclusively

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[DOCKER]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        print_status "Try: sudo systemctl start docker"
        exit 1
    fi
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
}

# Start all services
start_services() {
    print_status "Starting all services with Docker Compose..."
    
    # Check for .env file
    if [ ! -f .env ]; then
        print_warning ".env file not found. Creating from template..."
        echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env
        echo "DEFAULT_EXPIRE_SECONDS=30" >> .env
        echo "RATE_LIMIT_PER_USER=5" >> .env
        echo "LOG_LEVEL=INFO" >> .env
        print_warning "Please edit .env file and add your TELEGRAM_BOT_TOKEN"
    fi
    
    # Start services
    docker-compose up --build -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    check_services
}

# Check service health
check_services() {
    print_status "Checking service health..."
    
    # Check MongoDB
    if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        print_success "MongoDB is running"
    else
        print_warning "MongoDB is not responding"
    fi
    
    # Check Backend
    if curl -s http://localhost:5572/api/ > /dev/null 2>&1; then
        print_success "Backend API is running on http://localhost:5572"
    else
        print_warning "Backend API is not responding"
    fi
    
    # Check OTP Gateway
    if curl -s http://localhost:5571/health > /dev/null 2>&1; then
        print_success "OTP Gateway is running on http://localhost:5571"
    else
        print_warning "OTP Gateway is not responding (check TELEGRAM_BOT_TOKEN)"
    fi
    
    # Check Frontend
    if curl -s http://localhost:5573 > /dev/null 2>&1; then
        print_success "Frontend is running on http://localhost:5573"
    else
        print_warning "Frontend is not responding"
    fi
}

# Stop all services
stop_services() {
    print_status "Stopping all services..."
    docker-compose down
    print_success "All services stopped"
}

# Restart all services
restart_services() {
    print_status "Restarting all services..."
    docker-compose restart
    print_success "All services restarted"
}

# View logs
view_logs() {
    print_status "Showing logs for all services..."
    docker-compose logs -f
}

# Check status
check_status() {
    print_status "Checking service status..."
    docker-compose ps
    
    echo ""
    print_status "Service URLs:"
    echo "  Frontend:     http://localhost:5573"
    echo "  Backend API:  http://localhost:5572/api/"
    echo "  OTP Gateway:  http://localhost:5571"
    echo "  MongoDB:      localhost:5574"
    echo ""
    echo "  Backend Docs: http://localhost:5572/docs"
    echo "  OTP Docs:     http://localhost:5571/docs"
}

# Clean everything
clean_all() {
    print_status "Cleaning all Docker resources..."
    docker-compose down -v --rmi all
    docker system prune -f
    print_success "All Docker resources cleaned"
}

# Main function
main() {
    case "${1:-start}" in
        "start")
            check_docker
            check_docker_compose
            start_services
            ;;
        "stop")
            check_docker
            stop_services
            ;;
        "restart")
            check_docker
            check_docker_compose
            restart_services
            check_services
            ;;
        "logs")
            check_docker
            view_logs
            ;;
        "status")
            check_docker
            check_status
            ;;
        "clean")
            check_docker
            clean_all
            ;;
        "help"|"-h"|"--help")
            echo "Telega2Go Docker-Only Management Script"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start     Start all services (default)"
            echo "  stop      Stop all services"
            echo "  restart   Restart all services"
            echo "  logs      View logs for all services"
            echo "  status    Check service status"
            echo "  clean     Clean all Docker resources"
            echo "  help      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 start    # Start all services"
            echo "  $0 logs     # View logs"
            echo "  $0 status   # Check status"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
