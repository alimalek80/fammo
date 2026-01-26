#!/bin/bash

# FAMMO Backend Deployment Script
# This script helps synchronize the local development environment with cPanel production

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 FAMMO Backend Deployment Helper${NC}"
echo "================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Error: This script must be run from the project root directory${NC}"
    exit 1
fi

# Create backup of current migrations
echo -e "${YELLOW}📦 Creating backup of current migrations...${NC}"
timestamp=$(date +"%Y%m%d_%H%M%S")
mkdir -p "migration_backups/backup_$timestamp"
cp -r */migrations "migration_backups/backup_$timestamp/" 2>/dev/null || echo "No migrations to backup"

# Function to sync migrations from cPanel files
sync_migrations() {
    if [ -d "cpanel_files" ]; then
        echo -e "${YELLOW}🔄 Syncing migrations from cPanel files...${NC}"
        
        # List of apps to sync
        apps=("ai_core" "aihub" "api" "blog" "chat" "core" "evidence" "pet" "subscription" "userapp" "vets")
        
        for app in "${apps[@]}"; do
            if [ -d "cpanel_files/$app/migrations" ] && [ -d "$app/migrations" ]; then
                echo "  - Syncing $app migrations..."
                cp -f cpanel_files/$app/migrations/*.py "$app/migrations/" 2>/dev/null || true
            fi
        done
        
        echo -e "${GREEN}✅ Migrations synced${NC}"
    else
        echo -e "${YELLOW}⚠️  No cpanel_files directory found, skipping migration sync${NC}"
    fi
}

# Function to check environment
check_environment() {
    echo -e "${YELLOW}🔍 Checking environment...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${RED}❌ .env file not found!${NC}"
        echo "Creating .env from .env.example..."
        if [ -f ".env.example" ]; then
            cp ".env.example" ".env"
            echo -e "${YELLOW}⚠️  Please edit .env file with your configuration${NC}"
        else
            echo -e "${RED}❌ .env.example not found either!${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ Environment check completed${NC}"
}

# Function to run Django checks
django_check() {
    echo -e "${YELLOW}🔧 Running Django system checks...${NC}"
    
    python manage.py check
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Django checks passed${NC}"
    else
        echo -e "${RED}❌ Django checks failed${NC}"
        return 1
    fi
}

# Main deployment process
case "$1" in
    "sync")
        sync_migrations
        check_environment
        django_check
        echo -e "${GREEN}🎉 Synchronization completed!${NC}"
        ;;
    "check")
        check_environment
        django_check
        ;;
    "backup")
        echo -e "${GREEN}✅ Backup created in migration_backups/backup_$timestamp${NC}"
        ;;
    *)
        echo "Usage: $0 {sync|check|backup}"
        echo ""
        echo "Commands:"
        echo "  sync   - Sync migrations from cPanel and check environment"
        echo "  check  - Check environment and run Django checks"
        echo "  backup - Create backup of current migrations"
        echo ""
        echo "Example: ./deploy.sh sync"
        ;;
esac