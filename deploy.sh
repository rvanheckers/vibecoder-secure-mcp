#!/bin/bash
# VIBECODER-SECURE MCP - Production Deployment Script

set -euo pipefail

# Configuration
COMPOSE_FILE="production.yml"
SERVICE_NAME="vibecoder-mcp"
IMAGE_NAME="ghcr.io/vibecoder/vibecoder-secure-mcp:latest"
BACKUP_DIR="/opt/vibecoder/backups/$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Help function
show_help() {
    cat << EOF
🎯 VIBECODER-SECURE MCP Deployment Script

Usage: $0 [OPTION]

Options:
    deploy      Deploy/update the production service
    start       Start the production service
    stop        Stop the production service
    restart     Restart the production service
    status      Show service status
    logs        Show service logs
    backup      Create backup of current data
    rollback    Rollback to previous version
    health      Check service health
    help        Show this help message

Examples:
    $0 deploy       # Deploy latest version
    $0 status       # Check current status
    $0 logs         # View service logs
    $0 backup       # Create data backup

EOF
}

# Check prerequisites
check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    command -v docker >/dev/null 2>&1 || error "Docker is not installed"
    command -v docker-compose >/dev/null 2>&1 || error "Docker Compose is not installed"
    
    # Check if running as root or with docker group
    if ! docker info >/dev/null 2>&1; then
        error "Cannot access Docker. Run as root or add user to docker group"
    fi
    
    log "✅ Prerequisites check passed"
}

# Create necessary directories
setup_directories() {
    log "📁 Setting up directories..."
    
    sudo mkdir -p /opt/vibecoder/{data,docs,logs,backups}
    sudo chown -R $(whoami):$(whoami) /opt/vibecoder
    
    log "✅ Directories created"
}

# Backup current data
backup_data() {
    log "💾 Creating backup..."
    
    if [ -d "/opt/vibecoder/data" ]; then
        sudo mkdir -p "$BACKUP_DIR"
        sudo cp -r /opt/vibecoder/data "$BACKUP_DIR/"
        sudo cp -r /opt/vibecoder/docs "$BACKUP_DIR/" 2>/dev/null || true
        sudo cp -r /opt/vibecoder/logs "$BACKUP_DIR/" 2>/dev/null || true
        
        log "✅ Backup created at $BACKUP_DIR"
    else
        warn "No existing data to backup"
    fi
}

# Deploy service
deploy_service() {
    log "🚀 Deploying VIBECODER-SECURE MCP..."
    
    check_prerequisites
    setup_directories
    
    # Pull latest image
    log "📥 Pulling latest image..."
    docker pull "$IMAGE_NAME" || warn "Could not pull latest image, using local"
    
    # Create backup before deployment
    backup_data
    
    # Deploy with docker-compose
    log "🔧 Starting deployment..."
    docker-compose -f "$COMPOSE_FILE" up -d --remove-orphans
    
    # Wait for service to be healthy
    log "⏳ Waiting for service to be healthy..."
    for i in {1..30}; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up (healthy)"; then
            log "✅ Service is healthy!"
            break
        elif [ $i -eq 30 ]; then
            error "Service failed to become healthy after 5 minutes"
        else
            echo -n "."
            sleep 10
        fi
    done
    
    # Show final status
    show_status
    
    log "🎯 VIBECODER-SECURE MCP deployment completed successfully!"
}

# Start service
start_service() {
    log "🚀 Starting VIBECODER-SECURE MCP..."
    docker-compose -f "$COMPOSE_FILE" up -d
    log "✅ Service started"
}

# Stop service
stop_service() {
    log "🛑 Stopping VIBECODER-SECURE MCP..."
    docker-compose -f "$COMPOSE_FILE" down
    log "✅ Service stopped"
}

# Restart service
restart_service() {
    log "🔄 Restarting VIBECODER-SECURE MCP..."
    docker-compose -f "$COMPOSE_FILE" restart
    log "✅ Service restarted"
}

# Show status
show_status() {
    log "📊 Service Status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo
    log "📈 Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep vibecoder || true
}

# Show logs
show_logs() {
    log "📋 Service Logs:"
    docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
}

# Health check
health_check() {
    log "🏥 Checking service health..."
    
    # Check if container is running
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        error "Service is not running"
    fi
    
    # Check health endpoint
    if curl -f -s http://localhost:8000/health >/dev/null; then
        log "✅ Health check passed"
        
        # Get detailed status
        echo
        log "🎯 Vibecoder Status:"
        curl -s http://localhost:8000/health | python3 -m json.tool || true
    else
        error "Health check failed - service is not responding"
    fi
}

# Rollback to previous version
rollback() {
    log "⏪ Rolling back to previous version..."
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t /opt/vibecoder/backups/ | head -n1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        error "No backups found for rollback"
    fi
    
    log "📦 Found backup: $LATEST_BACKUP"
    
    # Stop current service
    stop_service
    
    # Restore data
    log "📥 Restoring data from backup..."
    sudo rm -rf /opt/vibecoder/data
    sudo cp -r "/opt/vibecoder/backups/$LATEST_BACKUP/data" /opt/vibecoder/
    sudo chown -R $(whoami):$(whoami) /opt/vibecoder
    
    # Start service
    start_service
    
    log "✅ Rollback completed"
}

# Main script logic
case "${1:-help}" in
    deploy)
        deploy_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    backup)
        backup_data
        ;;
    rollback)
        rollback
        ;;
    health)
        health_check
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown option: $1. Use '$0 help' for usage information."
        ;;
esac