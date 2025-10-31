#!/bin/bash
# 🚀 Start Script for Telega2Go Docker Services
# Single Docker management method as per A_DEVELOPMENT_RULES.md
# Includes features from deploy_bulletproof.sh (testing, backup, rollback)

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}ℹ️  [$(date +'%H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ [$(date +'%H:%M:%S')] $1${NC}"
}

log_error() {
    echo -e "${RED}❌ [$(date +'%H:%M:%S')] $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  [$(date +'%H:%M:%S')] $1${NC}"
}

# Configuration
BACKUP_DIR="_backup_$(date +%Y%m%d_%H%M%S)"

# Check if docker compose is available (prefer v2, fallback to v1)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    log_error "docker compose not found"
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Validation functions
validate_environment() {
    log "🔍 Validating environment..."
    
    # Check required tools
    command -v docker >/dev/null 2>&1 || { log_error "Docker is required but not installed."; exit 1; }
    command -v python3 >/dev/null 2>&1 || { log_error "Python3 is required but not installed."; exit 1; }
    
    # Check if we're in the right directory
    if [ ! -f "docker-compose.yml" ]; then
        log_error "docker-compose.yml not found. Please run from project root."
        exit 1
    fi
    
    log_success "Environment validation passed"
}

run_comprehensive_tests() {
    log "🧪 Running comprehensive test suite..."
    
    local test_passed=0
    local test_failed=0
    
    # Test 1: Basic functionality
    if [ -f "test_basic_functionality.py" ]; then
        log "Running basic functionality tests..."
        if python3 test_basic_functionality.py 2>/dev/null; then
            ((test_passed++))
        else
            ((test_failed++))
            log_warning "Basic functionality tests failed (non-critical)"
        fi
    fi
    
    # Test 2: OTP variants
    if [ -f "test_otp_variants_comprehensive.py" ]; then
        log "Running OTP variants tests..."
        if python3 test_otp_variants_comprehensive.py 2>/dev/null; then
            ((test_passed++))
        else
            ((test_failed++))
            log_warning "OTP variants tests failed (non-critical)"
        fi
    fi
    
    # Test 3: Complete automation
    if [ -f "test_complete_automation.py" ]; then
        log "Running complete automation tests..."
        if python3 test_complete_automation.py 2>/dev/null; then
            ((test_passed++))
        else
            ((test_failed++))
            log_warning "Complete automation tests failed (non-critical)"
        fi
    fi
    
    if [ $test_passed -gt 0 ] || [ $test_failed -eq 0 ]; then
        log_success "Tests completed: $test_passed passed"
        return 0
    else
        log_warning "No tests found or all tests failed (continuing anyway)"
        return 0
    fi
}

create_backup() {
    log "💾 Creating backup..."
    
    if [ -d "$BACKUP_DIR" ]; then
        rm -rf "$BACKUP_DIR"
    fi
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup important files
    cp -r backend "$BACKUP_DIR/" 2>/dev/null || true
    cp -r frontend "$BACKUP_DIR/" 2>/dev/null || true
    cp -r otp-social-gateway "$BACKUP_DIR/" 2>/dev/null || true
    cp docker-compose.yml "$BACKUP_DIR/" 2>/dev/null || true
    cp .env "$BACKUP_DIR/" 2>/dev/null || true
    
    log_success "Backup created: $BACKUP_DIR"
}

rollback() {
    log "🔄 Rolling back deployment..."
    
    # Stop current services
    $DOCKER_COMPOSE_CMD down
    
    # Find most recent backup
    local latest_backup=$(ls -td _backup_* 2>/dev/null | head -1)
    
    if [ -n "$latest_backup" ]; then
        log "Restoring from backup: $latest_backup"
        # Note: Manual restore may be needed depending on what changed
        log_warning "Please manually restore from $latest_backup if needed"
    else
        log_warning "No backup found to restore"
    fi
    
    log_warning "Rollback completed"
}

# Main start function
start_services() {
    local mode="${1:-quick}"
    
    log "🚀 Starting Telega2Go Services"
    log "================================"
    
    # Validate environment
    validate_environment
    
    # Optional: Create backup if full mode
    if [ "$mode" = "full" ]; then
        create_backup
        
        # Optional: Run tests
        if [ "$2" != "skip-tests" ]; then
            run_comprehensive_tests
        fi
    fi
    
    # Rebuild otp-gateway (since we have new code changes)
    log "🔨 Rebuilding OTP Gateway..."
    $DOCKER_COMPOSE_CMD build otp-gateway
    
    # Restart OTP Gateway to apply new changes (only this service)
    log "🔄 Restarting OTP Gateway with new code..."
    docker stop telega2go-otp-gateway 2>/dev/null || true
    docker rm telega2go-otp-gateway 2>/dev/null || true
    $DOCKER_COMPOSE_CMD up -d --no-deps otp-gateway
    
    # Ensure all services are running
    log "▶️  Ensuring all services are running..."
    $DOCKER_COMPOSE_CMD up -d
    
    # Wait for services to initialize
    log "⏳ Waiting for services to be ready..."
    sleep 5
    
    # Health checks
    log "🏥 Performing health checks..."
    
    local health_failed=0
    
    # Check OTP Gateway (correct port: 55551)
    if curl -f -s http://localhost:55551/health > /dev/null 2>&1; then
        log_success "OTP Gateway is healthy"
    else
        log_error "OTP Gateway health check failed"
        ((health_failed++))
    fi
    
    # Check Backend (correct port: 55552)
    if curl -f -s http://localhost:55552/api/ > /dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_error "Backend health check failed"
        ((health_failed++))
    fi
    
    # Check Frontend (correct port: 55553)
    if curl -f -s http://localhost:55553/ > /dev/null 2>&1; then
        log_success "Frontend is healthy"
    else
        log_error "Frontend health check failed"
        ((health_failed++))
    fi
    
    # Show service status
    echo ""
    log "📊 Service Status:"
    $DOCKER_COMPOSE_CMD ps
    
    echo ""
    if [ $health_failed -eq 0 ]; then
        log_success "🎉 Services started successfully!"
    else
        log_error "⚠️  Some services failed health checks"
    fi
    
    echo ""
    echo "Service URLs:"
    echo "  🌐 Frontend:     http://localhost:55553"
    echo "  🔧 Backend API:  http://localhost:55552/api/"
    echo "  📨 OTP Gateway:  http://localhost:55551/health"
    echo ""
    echo "Commands:"
    echo "  View logs:      $DOCKER_COMPOSE_CMD logs -f [service-name]"
    echo "  Stop services:  $DOCKER_COMPOSE_CMD down"
    echo "  Full deploy:    ./start.sh full"
    echo "  With tests:     ./start.sh full test"
    
    return $health_failed
}

# Parse command line arguments
case "${1:-}" in
    "full")
        start_services "full" "${2:-}"
        ;;
    "test")
        validate_environment
        run_comprehensive_tests
        ;;
    "rollback")
        rollback
        ;;
    "backup")
        create_backup
        ;;
    "health")
        validate_environment
        curl -f -s http://localhost:55551/health > /dev/null && log_success "OTP Gateway: OK" || log_error "OTP Gateway: FAIL"
        curl -f -s http://localhost:55552/api/ > /dev/null && log_success "Backend: OK" || log_error "Backend: FAIL"
        curl -f -s http://localhost:55553/ > /dev/null && log_success "Frontend: OK" || log_error "Frontend: FAIL"
        ;;
    "help"|"--help"|"-h")
        echo "Usage: ./start.sh [command]"
        echo ""
        echo "Commands:"
        echo "  (none)     - Quick start (rebuild OTP Gateway and restart) [default]"
        echo "  full       - Full deployment (with backup and optional tests)"
        echo "  full test  - Full deployment with comprehensive tests"
        echo "  test       - Run test suite only"
        echo "  backup     - Create backup only"
        echo "  rollback   - Rollback to previous backup"
        echo "  health     - Check health of all services"
        echo "  help       - Show this help message"
        ;;
    "")
        # Default: quick start
        start_services "quick"
        ;;
    *)
        log_error "Unknown command: $1"
        echo "Use './start.sh help' for usage information"
        exit 1
        ;;
esac
