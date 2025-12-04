#!/bin/bash
# Quick fix for Django testing on cPanel
# Run this script on your cPanel server via SSH

echo "Fixing Django test database configuration..."

cd ~/fammo

# Check if settings.py already has the test database fix
if grep -q "if 'test' in sys.argv:" famo/settings.py; then
    echo "✓ Test database configuration already exists"
else
    echo "Adding SQLite test database configuration..."
    
    # Backup settings.py
    cp famo/settings.py famo/settings.py.backup
    
    # Add the test database configuration after DATABASES
    # This will be inserted after the main DATABASES block
    sed -i "/^# DATABASE ON CPANEL HOST/i\\
\\
# Use SQLite for tests to avoid permission issues (especially on cPanel)\\
if 'test' in sys.argv:\\
    DATABASES = {\\
        'default': {\\
            'ENGINE': 'django.db.backends.sqlite3',\\
            'NAME': BASE_DIR / 'test_db.sqlite3',\\
        }\\
    }\\
" famo/settings.py
    
    echo "✓ Configuration added"
fi

# Test the configuration
echo ""
echo "Testing configuration..."
python manage.py test ai_core.tests.test_ai_serializers --verbosity=2

echo ""
echo "Done! If tests passed, the fix is working."
echo "The test database file will be at: ~/fammo/test_db.sqlite3"
