# 🚀 FAMMO Weight Notifications - cPanel Deployment

## Quick Start for cPanel Hosting

### 🎯 **Automatic Setup (Recommended)**
```bash
./cpanel_auto_setup.sh
```
This script detects your hosting environment and sets everything up automatically!

---

## 📋 Manual Setup Options

### **Option 1: VPS/Dedicated Server with Root Access**
```bash
# Start all services automatically
sudo systemctl start redis fammo-celery fammo-celery-beat
sudo systemctl enable redis fammo-celery fammo-celery-beat

# Check status
sudo systemctl status fammo-celery fammo-celery-beat
```

### **Option 2: VPS/Cloud Server (Limited Root)**
```bash
# Start services manually
./fammo_services.sh start

# Check status  
./fammo_services.sh status

# View logs
./fammo_services.sh logs
```

### **Option 3: Shared Hosting (Most Common)**
1. **Paths already configured** for your cPanel setup
2. **Add cron job** in cPanel → Cron Jobs:
   ```
   0 */6 * * * /home/fammkoqw/public_html/fammo/.venv/bin/python /home/fammkoqw/public_html/fammo/cron_weight_notifications.py
   ```
3. **Test**: `python cron_weight_notifications.py`

---

## 🧪 Testing

### Manual Check
```bash
# Test notification creation
python manage.py create_weight_notifications

# Test with dry run
python manage.py create_weight_notifications --dry-run
```

### Verify Notifications
1. Go to: `https://yourdomain.com/en/notifications/`
2. Login as pet owner
3. Check for weight update notifications

---

## 📊 How It Works

### **Automatic Schedule**
- **Daily at 1:30 AM**: Check all pets for weight updates
- **Immediate**: Notifications appear in user's notification center
- **Smart**: No duplicate notifications, auto-resolve when weight added

### **Notification Rules**
- **Dogs**: <6mo → 14 days, 6mo-7yr → 30 days, 7yr+ → 21 days
- **Cats**: <2mo → 7 days, 2mo-10yr → 30 days, 10yr+ → 21 days
- **First Weight**: Immediate notification if no weight records

---

## 🔧 Troubleshooting

### Common Issues
| Problem | Solution |
|---------|----------|
| ❌ Redis connection refused | Start Redis: `sudo systemctl start redis` |
| ❌ No notifications created | Check pet has birth_date and pet_type |
| ❌ Celery not running | Restart: `./fammo_services.sh restart` |
| ❌ Permission denied | Fix permissions: `chmod +x *.sh` |

### Debug Commands
```bash
# Check what pets need notifications
python manage.py shell -c "
from pet.models import Pet
for pet in Pet.objects.all():
    info = pet.get_weight_reminder_info()
    print(f'{pet.name}: {info[\"type\"] if info else \"none\"}'
)"

# View notification logs  
tail -f logs/weight_notifications.log

# Check cron jobs (shared hosting)
crontab -l
```

---

## 📁 File Reference

| File | Purpose |
|------|---------|
| `cpanel_auto_setup.sh` | 🎯 Auto-detect and setup everything |
| `fammo_services.sh` | ⚙️ Start/stop/monitor services (VPS) |
| `cron_weight_notifications.py` | ⏰ Cron job script (shared hosting) |
| `cpanel_deployment_guide.md` | 📚 Detailed deployment guide |
| `core/tasks.py` | 🧠 Main notification logic |

---

## ✅ Verification Checklist

- [ ] **Redis running** (VPS only): `redis-cli ping` returns `PONG`
- [ ] **Celery services running** (VPS): Check with status commands
- [ ] **Cron job added** (Shared): Listed in cPanel → Cron Jobs
- [ ] **Test successful**: `python manage.py create_weight_notifications`
- [ ] **Notifications visible**: Check `/en/notifications/` page
- [ ] **Logs working**: Check `logs/` directory for output

---

## 🆘 Support

### Production Deployment
1. **Upload all files** to your cPanel server
2. **Run** `./cpanel_auto_setup.sh`
3. **Follow prompts** for your hosting type
4. **Test** the system works
5. **Monitor logs** for any issues

### Need Help?
- 📋 Detailed guide: `cpanel_deployment_guide.md`
- 🔍 Debug: Check log files in `logs/` directory
- 🧪 Test: Use manual commands above

**🎉 Once set up, your users will automatically receive weight update notifications based on their pets' ages and weight tracking needs!**