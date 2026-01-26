#!/bin/bash

# FAMMO cPanel Deployment Safety Checklist
# Run this script on cPanel BEFORE pulling from Git

echo "🔒 FAMMO cPanel Pre-Deployment Safety Check"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: This script must be run from the project root directory"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Check database configuration
echo "🗄️  Database Configuration Check:"
if [ -f ".env" ]; then
    if grep -q "IS_CPANEL=True" .env && grep -q "USE_MYSQL=True" .env; then
        echo "✅ Environment correctly set for cPanel MySQL"
        echo "   IS_CPANEL=True ✓"
        echo "   USE_MYSQL=True ✓"
    else
        echo "⚠️  Environment variables need attention:"
        echo "   Current IS_CPANEL: $(grep IS_CPANEL .env || echo 'NOT SET')"
        echo "   Current USE_MYSQL: $(grep USE_MYSQL .env || echo 'NOT SET')"
        echo ""
        echo "❗ IMPORTANT: After git pull, make sure your .env has:"
        echo "   IS_CPANEL=True"
        echo "   USE_MYSQL=True"
        echo "   Plus your database credentials"
    fi
else
    echo "❌ No .env file found! You'll need to create one after git pull"
fi
echo ""

# Check current migration status
echo "🔄 Migration Status Check:"
echo "Checking current applied migrations..."
python manage.py showmigrations --plan | grep '\[X\]' | wc -l | xargs echo "Applied migrations count:"

# Check for unapplied migrations before pull
echo ""
echo "Checking for unapplied migrations..."
if python manage.py showmigrations --plan | grep -q '\[ \]'; then
    echo "⚠️  You have unapplied migrations. Apply them first:"
    echo "   python manage.py migrate"
    echo ""
    echo "Unapplied migrations:"
    python manage.py showmigrations --plan | grep '\[ \]' | head -5
else
    echo "✅ All current migrations are applied"
fi
echo ""

# Database backup reminder
echo "💾 Database Backup Reminder:"
echo "Before proceeding with git pull, ensure you have:"
echo "1. ✅ Recent database backup (via phpMyAdmin export)"
echo "2. ✅ File system backup of your project"
echo "3. ✅ Noted your current .env configuration"
echo ""

# Final safety check
echo "🚨 CRITICAL SAFETY POINTS:"
echo "1. The git pull will NOT affect your MySQL database data"
echo "2. Only code files and migration files will be updated"
echo "3. After git pull, you may need to run 'python manage.py migrate'"
echo "4. Your .env file with database credentials must be preserved"
echo ""

echo "Ready to proceed with git pull? (Make sure backups are done!)"