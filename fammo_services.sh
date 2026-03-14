#!/bin/bash
# FAMMO Services Startup Script for cPanel
# This script starts Redis, Celery Worker, and Celery Beat for automatic notifications

# =============================================================================
# CONFIGURATION - CONFIGURED FOR YOUR CPANEL
# =============================================================================
FAMMO_DIR="/home/fammkoqw/public_html/fammo"
VENV_PATH="$FAMMO_DIR/.venv/bin/activate"
REDIS_CONFIG="/home/fammkoqw/redis.conf"  # Optional custom Redis config
LOG_DIR="$FAMMO_DIR/logs"

# PID files to track processes
PIDFILE_REDIS="$FAMMO_DIR/redis.pid"
PIDFILE_WORKER="$FAMMO_DIR/celery_worker.pid"
PIDFILE_BEAT="$FAMMO_DIR/celery_beat.pid"

# =============================================================================
# FUNCTIONS
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create necessary directories
setup_directories() {
    mkdir -p "$LOG_DIR"
    mkdir -p "$(dirname "$PIDFILE_REDIS")"
    print_status "Created log and PID directories"
}

# Check if a process is running by PID file
is_running() {
    local pidfile="$1"
    [ -f "$pidfile" ] && ps -p "$(cat "$pidfile")" > /dev/null 2>&1
}

# Start Redis server
start_redis() {
    print_status "Starting Redis server..."
    
    if is_running "$PIDFILE_REDIS"; then
        print_warning "Redis is already running"
        return 0
    fi
    
    # Try to start Redis
    if command -v redis-server &> /dev/null; then
        # Use custom config if available, otherwise use defaults
        if [ -f "$REDIS_CONFIG" ]; then
            redis-server "$REDIS_CONFIG" --daemonize yes --pidfile "$PIDFILE_REDIS" --logfile "$LOG_DIR/redis.log"
        else
            redis-server --daemonize yes --pidfile "$PIDFILE_REDIS" --logfile "$LOG_DIR/redis.log" --port 6379
        fi
        
        sleep 2
        
        if is_running "$PIDFILE_REDIS"; then
            print_success "Redis started successfully"
            return 0
        else
            print_error "Failed to start Redis"
            return 1
        fi
    else
        print_error "Redis not installed. Install with: sudo apt install redis-server OR sudo yum install redis"
        return 1
    fi
}

# Start Celery Worker
start_worker() {
    print_status "Starting Celery Worker..."
    
    if is_running "$PIDFILE_WORKER"; then
        print_warning "Celery Worker is already running"
        return 0
    fi
    
    cd "$FAMMO_DIR" || { print_error "Cannot change to $FAMMO_DIR"; return 1; }
    source "$VENV_PATH" || { print_error "Cannot activate virtual environment"; return 1; }
    
    nohup celery -A famo worker \
        --loglevel=info \
        --pidfile="$PIDFILE_WORKER" \
        --logfile="$LOG_DIR/celery_worker.log" \
        --detach \
        --concurrency=2 > /dev/null 2>&1
    
    sleep 3
    
    if is_running "$PIDFILE_WORKER"; then
        print_success "Celery Worker started successfully"
        return 0
    else
        print_error "Failed to start Celery Worker"
        return 1
    fi
}

# Start Celery Beat
start_beat() {
    print_status "Starting Celery Beat scheduler..."
    
    if is_running "$PIDFILE_BEAT"; then
        print_warning "Celery Beat is already running"
        return 0
    fi
    
    cd "$FAMMO_DIR" || { print_error "Cannot change to $FAMMO_DIR"; return 1; }
    source "$VENV_PATH" || { print_error "Cannot activate virtual environment"; return 1; }
    
    nohup celery -A famo beat \
        --loglevel=info \
        --scheduler django_celery_beat.schedulers:DatabaseScheduler \
        --pidfile="$PIDFILE_BEAT" \
        --logfile="$LOG_DIR/celery_beat.log" \
        --detach > /dev/null 2>&1 &
    
    # Save the PID manually since --detach might not work for beat
    echo $! > "$PIDFILE_BEAT"
    
    sleep 3
    
    if is_running "$PIDFILE_BEAT"; then
        print_success "Celery Beat started successfully"
        return 0
    else
        print_error "Failed to start Celery Beat"
        return 1
    fi
}

# Stop a service
stop_service() {
    local service_name="$1"
    local pidfile="$2"
    
    if is_running "$pidfile"; then
        print_status "Stopping $service_name..."
        local pid=$(cat "$pidfile")
        kill "$pid" 2>/dev/null
        
        # Wait for process to stop
        for i in {1..10}; do
            if ! is_running "$pidfile"; then
                rm -f "$pidfile"
                print_success "$service_name stopped"
                return 0
            fi
            sleep 1
        done
        
        # Force kill if still running
        kill -9 "$pid" 2>/dev/null
        rm -f "$pidfile"
        print_warning "$service_name force stopped"
    else
        print_warning "$service_name is not running"
    fi
}

# Check status of all services
check_status() {
    echo "=== FAMMO Services Status ==="
    
    if is_running "$PIDFILE_REDIS"; then
        print_success "Redis: Running (PID: $(cat "$PIDFILE_REDIS"))"
    else
        print_error "Redis: Not running"
    fi
    
    if is_running "$PIDFILE_WORKER"; then
        print_success "Celery Worker: Running (PID: $(cat "$PIDFILE_WORKER"))"
    else
        print_error "Celery Worker: Not running"
    fi
    
    if is_running "$PIDFILE_BEAT"; then
        print_success "Celery Beat: Running (PID: $(cat "$PIDFILE_BEAT"))"
    else
        print_error "Celery Beat: Not running"
    fi
    
    echo ""
    echo "Log files location: $LOG_DIR"
    echo "To test notifications manually: cd $FAMMO_DIR && python manage.py create_weight_notifications"
}

# Test the notification system
test_notifications() {
    print_status "Testing weight notification system..."
    cd "$FAMMO_DIR" || { print_error "Cannot change to $FAMMO_DIR"; return 1; }
    source "$VENV_PATH" || { print_error "Cannot activate virtual environment"; return 1; }
    
    python manage.py create_weight_notifications
}

# =============================================================================
# MAIN SCRIPT
# =============================================================================

case "$1" in
    start)
        print_status "Starting FAMMO notification services..."
        setup_directories
        
        start_redis
        redis_status=$?
        
        if [ $redis_status -eq 0 ]; then
            start_worker
            start_beat
            echo ""
            check_status
            echo ""
            print_success "All services started! Weight notifications will run automatically daily at 1:30 AM"
            print_status "To monitor logs: tail -f $LOG_DIR/*.log"
        else
            print_error "Cannot start Celery services without Redis"
            exit 1
        fi
        ;;
    
    stop)
        print_status "Stopping FAMMO notification services..."
        stop_service "Celery Beat" "$PIDFILE_BEAT"
        stop_service "Celery Worker" "$PIDFILE_WORKER"
        stop_service "Redis" "$PIDFILE_REDIS"
        print_success "All services stopped"
        ;;
    
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    
    status)
        check_status
        ;;
    
    test)
        test_notifications
        ;;
    
    logs)
        print_status "Recent log entries:"
        echo "=== Redis Log ==="
        tail -10 "$LOG_DIR/redis.log" 2>/dev/null || echo "No Redis log found"
        echo ""
        echo "=== Celery Worker Log ==="
        tail -10 "$LOG_DIR/celery_worker.log" 2>/dev/null || echo "No Worker log found"
        echo ""
        echo "=== Celery Beat Log ==="
        tail -10 "$LOG_DIR/celery_beat.log" 2>/dev/null || echo "No Beat log found"
        ;;
    
    *)
        echo "FAMMO Weight Notification Services Manager"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|test|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start Redis, Celery Worker, and Celery Beat"
        echo "  stop    - Stop all services"
        echo "  restart - Restart all services"
        echo "  status  - Show status of all services"
        echo "  test    - Manually run weight notification check"
        echo "  logs    - Show recent log entries"
        echo ""
        echo "Before first use:"
        echo "1. Update the paths at the top of this script"
        echo "2. Make sure Redis and Python virtual environment are installed"
        echo "3. Run: chmod +x $0"
        echo "4. Start services: $0 start"
        exit 1
        ;;
esac