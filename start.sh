#!/bin/bash

# Telega2Go Startup Script
# SINGLE ENTRY POINT for ALL Docker operations
# This script handles starting, rebuilding, and managing all components

set -e

# Parse command line arguments
FORCE_REBUILD=false
CLEAN_BUILD=false
SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --force-rebuild|-f)
            FORCE_REBUILD=true
            shift
            ;;
        --clean|-c)
            CLEAN_BUILD=true
            shift
            ;;
        --service|-s)
            SERVICE="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --force-rebuild, -f    Force rebuild without cache"
            echo "  --clean, -c           Clean build (remove images first)"
            echo "  --service, -s SERVICE Rebuild specific service only"
            echo "  --help, -h            Show this help"
            echo ""
            echo "Examples:"
            echo "  $0                    # Normal start"
            echo "  $0 --force-rebuild    # Force rebuild all services"
            echo "  $0 --clean            # Clean build (remove images first)"
            echo "  $0 --service frontend # Rebuild only frontend"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🚀 Starting Telega2Go Project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
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
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available (prefer newer docker compose)
if ! command -v docker > /dev/null 2>&1; then
    print_error "Docker is not installed. Please install Docker and try again."
    exit 1
fi

# Use newer docker compose if available, fallback to docker-compose
if docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

# Check for .env file
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        print_warning "Please edit .env file and add your TELEGRAM_BOT_TOKEN"
        print_warning "Get your bot token from @BotFather on Telegram"
    else
        print_error ".env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

# Check if TELEGRAM_BOT_TOKEN is set
if grep -q "your_bot_token_here" .env; then
    print_warning "TELEGRAM_BOT_TOKEN is not set in .env file"
    print_warning "Please edit .env file and add your bot token from @BotFather"
    print_warning "Continuing with dummy token for now..."
fi

# Handle different build scenarios
if [ "$CLEAN_BUILD" = true ]; then
    print_status "Cleaning build (removing images first)..."
    $DOCKER_COMPOSE_CMD down --rmi all 2>/dev/null || true
    docker system prune -f
fi

if [ "$FORCE_REBUILD" = true ]; then
    print_status "Force rebuilding all services (no cache)..."
    if [ -n "$SERVICE" ]; then
        print_status "Rebuilding service: $SERVICE"
        $DOCKER_COMPOSE_CMD build --no-cache $SERVICE
        $DOCKER_COMPOSE_CMD up -d $SERVICE
    else
        $DOCKER_COMPOSE_CMD build --no-cache
        $DOCKER_COMPOSE_CMD up -d
    fi
elif [ -n "$SERVICE" ]; then
    print_status "Rebuilding service: $SERVICE"
    $DOCKER_COMPOSE_CMD up --build -d $SERVICE
else
    print_status "Building and starting all services..."
    $DOCKER_COMPOSE_CMD up --build -d
fi

print_status "Waiting for services to be ready..."

# Wait for services to be healthy
sleep 10

# Check service health
print_status "Checking service health..."

# Check MongoDB
if $DOCKER_COMPOSE_CMD exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
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

echo ""
print_success "🎉 Telega2Go is starting up!"
echo ""
echo "📋 Service URLs:"
echo "  Frontend:     http://localhost:5573"
echo "  Backend API:  http://localhost:5572/api/"
echo "  OTP Gateway:  http://localhost:5571"
echo "  MongoDB:      localhost:5574"
echo ""
echo "📚 API Documentation:"
echo "  Backend:      http://localhost:5572/docs"
echo "  OTP Gateway:  http://localhost:5571/docs"
echo ""
echo "🔧 Management Commands:"
echo "  View logs:    $DOCKER_COMPOSE_CMD logs -f"
echo "  Stop all:     $DOCKER_COMPOSE_CMD down"
echo "  Restart:      $DOCKER_COMPOSE_CMD restart"
echo ""
echo "🚀 Enhanced Start Commands:"
echo "  ./start.sh                    # Normal start"
echo "  ./start.sh --force-rebuild    # Force rebuild (fixes cache issues)"
echo "  ./start.sh --clean            # Clean build (removes all images)"
echo "  ./start.sh --service frontend # Rebuild only frontend"
echo "  ./start.sh --help             # Show all options"
echo ""
print_warning "Note: If OTP Gateway is not working, check your TELEGRAM_BOT_TOKEN in .env file"
print_warning "Note: Use --force-rebuild if you're having cache issues with frontend updates"
