#!/bin/bash
# FAMMO cPanel Auto-Setup Script
# This script automatically configures weight notifications for different cPanel environments

echo "🚀 FAMMO Weight Notifications Auto-Setup for cPanel"
echo "=================================================="

# Detect hosting environment
detect_environment() {
    if command -v redis-server &> /dev/null && [ -w /etc/systemd/system ]; then
        echo "VPS/Dedicated Server with root access detected"
        return 0
    elif command -v redis-server &> /dev/null; then
        echo "VPS with Redis but limited system access detected"
        return 1
    else
        echo "Shared hosting environment detected"
        return 2
    fi
}

# Get user input for paths
get_user_config() {
    echo ""
    echo "📁 Please provide the following information:"
    
    # Get current directory as default
    CURRENT_DIR=$(pwd)
    
    read -p "FAMMO project directory [$CURRENT_DIR]: " PROJECT_DIR
    PROJECT_DIR=${PROJECT_DIR:-$CURRENT_DIR}
    
    read -p "Your cPanel username: " USERNAME
    
    read -p "Your domain (e.g., yourdomain.com): " DOMAIN
    
    echo ""
    echo "Configuration:"
    echo "📂 Project Directory: $PROJECT_DIR"
    echo "👤 Username: $USERNAME"
    echo "🌐 Domain: $DOMAIN"
    echo ""
    
    read -p "Is this correct? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
}

# Setup for VPS/Dedicated Server (Option 1)
setup_vps_full() {
    echo ""
    echo "🔧 Setting up VPS/Dedicated server configuration..."
    
    # Install Redis if needed
    if ! command -v redis-server &> /dev/null; then
        echo "Installing Redis..."
        if [ -f /etc/redhat-release ]; then
            sudo yum install redis -y
        else
            sudo apt update && sudo apt install redis-server -y
        fi
    fi
    
    # Create systemd service files
    echo "Creating systemd service files..."
    
    # Celery Worker Service
    sudo tee /etc/systemd/system/fammo-celery.service > /dev/null <<EOF
[Unit]
Description=FAMMO Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=${USERNAME}
Group=${USERNAME}
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=${PROJECT_DIR}/.venv/bin
ExecStart=${PROJECT_DIR}/.venv/bin/celery multi start worker1 -A famo --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n.log --loglevel=INFO
ExecStop=${PROJECT_DIR}/.venv/bin/celery multi stopwait worker1 --pidfile=/var/run/celery/%n.pid
ExecReload=${PROJECT_DIR}/.venv/bin/celery multi restart worker1 -A famo --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n.log --loglevel=INFO

[Install]
WantedBy=multi-user.target
EOF

    # Celery Beat Service
    sudo tee /etc/systemd/system/fammo-celery-beat.service > /dev/null <<EOF
[Unit]
Description=FAMMO Celery Beat Scheduler
After=network.target redis.service

[Service]
Type=simple
User=${USERNAME}
Group=${USERNAME}
WorkingDirectory=${PROJECT_DIR}
Environment=PATH=${PROJECT_DIR}/.venv/bin
ExecStart=${PROJECT_DIR}/.venv/bin/celery -A famo beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Create directories and set permissions
    sudo mkdir -p /var/run/celery /var/log/celery
    sudo chown ${USERNAME}:${USERNAME} /var/run/celery /var/log/celery
    
    # Enable and start services
    sudo systemctl daemon-reload
    sudo systemctl enable redis fammo-celery fammo-celery-beat
    sudo systemctl start redis fammo-celery fammo-celery-beat
    
    echo "✅ VPS setup complete! Services are now running automatically."
    echo "📊 Check status with: sudo systemctl status fammo-celery fammo-celery-beat"
}

# Setup for VPS with limited access (Option 2)
setup_vps_limited() {
    echo ""
    echo "🔧 Setting up VPS with limited access configuration..."
    
    # Update the service script with user's paths
    sed -i "s|/home/yourusername/fammo-backend|${PROJECT_DIR}|g" "${PROJECT_DIR}/fammo_services.sh"
    chmod +x "${PROJECT_DIR}/fammo_services.sh"
    
    # Start services
    "${PROJECT_DIR}/fammo_services.sh" start
    
    # Add to user's crontab for auto-start on reboot
    (crontab -l 2>/dev/null; echo "@reboot ${PROJECT_DIR}/fammo_services.sh start") | crontab -
    
    echo "✅ VPS limited setup complete!"
    echo "📊 Check status with: ${PROJECT_DIR}/fammo_services.sh status"
    echo "🔄 Services will auto-start on server reboot"
}

# Setup for Shared Hosting (Option 3)
setup_shared_hosting() {
    echo ""
    echo "🔧 Setting up shared hosting configuration..."
    
    # Update cron script with user's paths
    sed -i "s|/home/yourusername/public_html/fammo-backend|${PROJECT_DIR}|g" "${PROJECT_DIR}/cron_weight_notifications.py"
    sed -i "s|/home/yourusername/fammo-backend/logs|${PROJECT_DIR}/logs|g" "${PROJECT_DIR}/cron_weight_notifications.py"
    
    # Make executable
    chmod +x "${PROJECT_DIR}/cron_weight_notifications.py"
    
    # Create logs directory
    mkdir -p "${PROJECT_DIR}/logs"
    
    # Test the script
    echo "🧪 Testing the notification script..."
    cd "${PROJECT_DIR}"
    python cron_weight_notifications.py
    
    echo ""
    echo "✅ Shared hosting setup complete!"
    echo ""
    echo "📋 NEXT STEPS:"
    echo "1. Go to your cPanel → Cron Jobs"
    echo "2. Add a new cron job with this command:"
    echo "   0 */6 * * * ${PROJECT_DIR}/.venv/bin/python ${PROJECT_DIR}/cron_weight_notifications.py"
    echo "3. This will check for weight notifications every 6 hours"
    echo ""
    echo "🧪 To test manually run:"
    echo "   cd ${PROJECT_DIR} && python cron_weight_notifications.py"
}

# Update Django settings for notifications in shared hosting
update_django_settings() {
    echo ""
    echo "🐍 Updating Django settings for better compatibility..."
    
    # Check if settings need modification for database-only celery
    if ! grep -q "CELERY_BROKER_URL.*redis" "${PROJECT_DIR}/famo/settings.py" 2>/dev/null; then
        echo "Settings already configured for database broker"
        return
    fi
    
    echo "Would you like to use database instead of Redis for task queue? (Good for shared hosting)"
    read -p "(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Backup original settings
        cp "${PROJECT_DIR}/famo/settings.py" "${PROJECT_DIR}/famo/settings.py.backup"
        
        # Update settings for database broker
        cat >> "${PROJECT_DIR}/famo/settings.py" << 'EOF'

# Alternative Celery configuration for shared hosting
# Uncomment these lines and comment out Redis configuration above
# CELERY_BROKER_URL = 'db+sqlite:///celery.db'
# CELERY_RESULT_BACKEND = 'db+sqlite:///celery_results.db'
EOF
        
        echo "✅ Settings updated. You can manually switch to database broker if needed."
    fi
}

# Main setup flow
main() {
    get_user_config
    
    detect_environment
    ENV_TYPE=$?
    
    case $ENV_TYPE in
        0)
            echo "🎯 Recommended: Full VPS setup with systemd services"
            setup_vps_full
            ;;
        1)
            echo "🎯 Recommended: VPS setup with custom service management"
            setup_vps_limited
            ;;
        2)
            echo "🎯 Recommended: Shared hosting setup with cron jobs"
            setup_shared_hosting
            ;;
    esac
    
    update_django_settings
    
    echo ""
    echo "🎉 FAMMO Weight Notifications Setup Complete!"
    echo ""
    echo "📚 What happens now:"
    echo "   • System checks pets daily for weight updates"
    echo "   • Sends notifications for missing/overdue weights"
    echo "   • Users see notifications at: https://${DOMAIN}/en/notifications/"
    echo "   • Notifications auto-resolve when users add weights"
    echo ""
    echo "🔍 Monitoring:"
    echo "   • Check logs in: ${PROJECT_DIR}/logs/"
    echo "   • Test manually: cd ${PROJECT_DIR} && python manage.py create_weight_notifications"
    echo ""
    echo "❓ Need help? Check cpanel_deployment_guide.md for detailed instructions"
}

# Run main function
main