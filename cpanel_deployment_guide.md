# cPanel Deployment Guide for FAMMO Weight Notifications

## Option 1: VPS/Dedicated Server with cPanel (Recommended)

### 1. Install Redis
```bash
# SSH into your server
sudo yum install redis -y  # CentOS/RHEL
# OR
sudo apt install redis-server -y  # Ubuntu/Debian

# Enable Redis to start on boot
sudo systemctl enable redis
sudo systemctl start redis

# Test Redis connection
redis-cli ping  # Should return "PONG"
```

### 2. Create Systemd Service Files

**Create Celery Worker Service:**
```bash
sudo nano /etc/systemd/system/fammo-celery.service
```

**Content for fammo-celery.service:**
```ini
[Unit]
Description=FAMMO Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=fammkoqw
Group=fammkoqw
EnvironmentFile=/home/fammkoqw/public_html/fammo/.env
WorkingDirectory=/home/fammkoqw/public_html/fammo
ExecStart=/home/fammkoqw/public_html/fammo/.venv/bin/celery multi start worker1 \
  -A famo --pidfile=/var/run/celery/%%n.pid \
  --logfile=/var/log/celery/%%n%%I.log --loglevel=INFO
ExecStop=/home/fammkoqw/public_html/fammo/.venv/bin/celery multi stopwait worker1 \
  --pidfile=/var/run/celery/%%n.pid
ExecReload=/home/fammkoqw/public_html/fammo/.venv/bin/celery multi restart worker1 \
  -A famo --pidfile=/var/run/celery/%%n.pid \
  --logfile=/var/log/celery/%%n%%I.log --loglevel=INFO

[Install]
WantedBy=multi-user.target
```

**Create Celery Beat Service:**
```bash
sudo nano /etc/systemd/system/fammo-celery-beat.service
```

**Content for fammo-celery-beat.service:**
```ini
[Unit]
Description=FAMMO Celery Beat Scheduler
After=network.target redis.service

[Service]
Type=simple
User=fammkoqw
Group=fammkoqw
EnvironmentFile=/home/fammkoqw/public_html/fammo/.env
WorkingDirectory=/home/fammkoqw/public_html/fammo
ExecStart=/home/fammkoqw/public_html/fammo/.venv/bin/celery -A famo beat \
  --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. Create Required Directories and Set Permissions
```bash
sudo mkdir -p /var/run/celery /var/log/celery
sudo chown fammkoqw:fammkoqw /var/run/celery /var/log/celery
```

### 4. Enable and Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable fammo-celery fammo-celery-beat
sudo systemctl start fammo-celery fammo-celery-beat

# Check status
sudo systemctl status fammo-celery
sudo systemctl status fammo-celery-beat
```

---

## Option 2: Shared Hosting with cPanel (Limited)

###⚠️ Limitations:
- Most shared hosting doesn't allow Redis or long-running processes
- Background services are usually restricted

### Alternative Solution: Enhanced Cron Jobs

**Create cron script:**
```bash
nano /home/fammkoqw/public_html/fammo/cron_weight_notifications.py
```

**Content:**
```python
#!/usr/bin/env python
"""
Enhanced cron job script for weight notifications on shared hosting
Run every hour to check pets needing weight updates
"""
import os
import sys
import django
from datetime import datetime, timedelta
import logging

# Setup Django
sys.path.append('/home/fammkoqw/public_html/fammo')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'famo.settings')
django.setup()

from pet.models import Pet
from core.models import UserNotification, NotificationType
from django.urls import reverse
from django.utils import timezone

# Setup logging
logging.basicConfig(
    filename='/home/fammkoqw/public_html/fammo/logs/weight_notifications.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_and_create_notifications():
    """Check pets and create weight notifications"""
    try:
        created_count = 0
        checked_count = 0
        
        # Get all pets with proper setup
        pets = Pet.objects.filter(
            birth_date__isnull=False,
            pet_type__isnull=False
        ).select_related('user', 'pet_type').prefetch_related('weight_records')
        
        for pet in pets:
            checked_count += 1
            
            # Check if pet needs weight reminder
            reminder_info = pet.get_weight_reminder_info()
            if not reminder_info:
                continue
            
            reminder_type = reminder_info['type']
            
            # Check for existing unread notifications to prevent duplicates
            notification_titles = []
            if reminder_type == 'first_weight':
                notification_titles = [f"Add {pet.name}'s first weight record"]
            elif reminder_type == 'overdue':
                notification_titles = [f"Update {pet.name}'s weight"]
            
            existing = UserNotification.objects.filter(
                user=pet.user,
                is_read=False,
                notification_type=NotificationType.PET_REMINDER,
                title__in=notification_titles
            ).exists()
            
            if existing:
                continue
            
            # Create notification
            if reminder_type == 'first_weight':
                title = f"Add {pet.name}'s first weight record"
                message = f"Tracking weight helps detect health changes early. Add the first weight record for {pet.name}."
                action_required = True
            elif reminder_type == 'overdue':
                days_overdue = reminder_info.get('days_overdue', 0)
                total_days = days_overdue + reminder_info['reminder_days']
                title = f"Update {pet.name}'s weight"
                message = f"It has been {total_days} days since {pet.name}'s last weight update. Regular tracking helps catch health changes early."
                action_required = False
            
            # Generate link
            link = reverse('pet:add_weight_record', args=[pet.id])
            
            # Create notification
            UserNotification.create_notification(
                user=pet.user,
                notification_type=NotificationType.PET_REMINDER,
                title=title,
                message=message,
                link=link,
                action_required=action_required,
                is_important=False
            )
            
            created_count += 1
            logging.info(f"Created weight notification for pet '{pet.name}' (ID: {pet.id}, Type: {reminder_type})")
        
        logging.info(f"Weight notification check completed: {created_count} created, {checked_count} total checked")
        return created_count
        
    except Exception as e:
        logging.error(f"Error in weight notification check: {str(e)}")
        return 0

if __name__ == "__main__":
    created = check_and_create_notifications()
    print(f"Created {created} weight notifications")
```

**Make it executable:**
```bash
chmod +x /home/fammkoqw/public_html/fammo/cron_weight_notifications.py
```

### Setup Cron Job in cPanel:
1. Go to cPanel → **Cron Jobs**
2. Add this cron job to run every 6 hours:
```
0 */6 * * * /home/fammkoqw/public_html/fammo/.venv/bin/python /home/fammkoqw/public_html/fammo/cron_weight_notifications.py
```

---

## Option 3: Cloud Services (Alternative)

### Using External Task Queue Services:
1. **Redis Cloud**: https://redislabs.com/
2. **Amazon SQS** with django-celery-sqs
3. **Database-only approach** (no Redis needed)

### Database-Only Solution:
Replace Redis with database task queue by modifying settings:

```python
# In settings.py
CELERY_BROKER_URL = 'db+sqlite:///celery.db'
CELERY_RESULT_BACKEND = 'db+sqlite:///celery_results.db'
```

---

## Option 4: Process Management Scripts

**Create supervisor-like script:**
```bash
nano /home/fammkoqw/public_html/fammo/start_services.sh
```

**Content:**
```bash
#!/bin/bash
# Start services script for cPanel

FAMMO_DIR="/home/fammkoqw/public_html/fammo"
VENV_PATH="$FAMMO_DIR/.venv/bin/activate"
PIDFILE_WORKER="$FAMMO_DIR/celery_worker.pid"
PIDFILE_BEAT="$FAMMO_DIR/celery_beat.pid"

# Function to start Celery Worker
start_worker() {
    cd $FAMMO_DIR
    source $VENV_PATH
    nohup celery -A famo worker --loglevel=info --pidfile=$PIDFILE_WORKER > worker.log 2>&1 &
    echo "Celery Worker started with PID: $!"
}

# Function to start Celery Beat
start_beat() {
    cd $FAMMO_DIR
    source $VENV_PATH
    nohup celery -A famo beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler --pidfile=$PIDFILE_BEAT > beat.log 2>&1 &
    echo "Celery Beat started with PID: $!"
}

# Check if Redis is running
redis-cli ping || { echo "Redis is not running. Please start Redis first."; exit 1; }

# Start services
start_worker
start_beat

echo "Services started. Check logs: worker.log and beat.log"
```

**Make executable and run:**
```bash
chmod +x start_services.sh
./start_services.sh
```

---

## Monitoring and Logs

### Check Service Status:
```bash
# Check if processes are running
ps aux | grep celery
ps aux | grep redis

# Check logs
tail -f /var/log/celery/worker1.log
tail -f /home/fammkoqw/public_html/fammo/beat.log

# Test notification creation
python manage.py create_weight_notifications
```

### Auto-restart on Server Reboot:
Add to crontab:
```bash
crontab -e
# Add this line:
@reboot /home/fammkoqw/public_html/fammo/start_services.sh
```

---

## Troubleshooting

### Common Issues:
1. **Redis connection refused**: Check if Redis is running
2. **Permission denied**: Check file permissions and ownership
3. **ImportError**: Ensure virtual environment is activated

### Quick Fix Commands:
```bash
# Restart services
sudo systemctl restart fammo-celery fammo-celery-beat

# Check Redis status
sudo systemctl status redis

# Manual notification creation
python manage.py create_weight_notifications
```

Choose the option that matches your cPanel hosting type:
- **VPS/Dedicated**: Use Option 1 (systemd services)
- **Shared Hosting**: Use Option 2 (cron jobs)
- **Cloud Hosting**: Use Option 3 (external services)