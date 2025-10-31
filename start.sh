#!/bin/bash
# 🚀 Start Script for Telega2Go Docker Services
# Single Docker management method as per A_DEVELOPMENT_RULES.md

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Telega2Go Services${NC}"
echo "================================"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found${NC}"
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Rebuild otp-gateway (since we have new code changes)
echo -e "${YELLOW}🔨 Rebuilding OTP Gateway with new inline query feature...${NC}"
docker-compose build otp-gateway

# Start all services
echo -e "${YELLOW}▶️  Starting all services...${NC}"
docker-compose up -d

# Wait for services to initialize
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Health checks
echo -e "${YELLOW}🏥 Performing health checks...${NC}"

# Check OTP Gateway
if curl -f -s http://localhost:55551/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ OTP Gateway is healthy${NC}"
else
    echo -e "${RED}❌ OTP Gateway health check failed${NC}"
fi

# Check Backend
if curl -f -s http://localhost:55552/api/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
fi

# Check Frontend
if curl -f -s http://localhost:55553/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend is healthy${NC}"
else
    echo -e "${RED}❌ Frontend health check failed${NC}"
fi

# Show service status
echo ""
echo -e "${GREEN}📊 Service Status:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}🎉 Services started!${NC}"
echo ""
echo "Service URLs:"
echo "  🌐 Frontend:     http://localhost:55553"
echo "  🔧 Backend API:  http://localhost:55552/api/"
echo "  📨 OTP Gateway:  http://localhost:55551/health"
echo ""
echo "To view logs: docker-compose logs -f [service-name]"
echo "To stop:      docker-compose down"

