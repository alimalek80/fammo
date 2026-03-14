# 🚀 START HERE - FAMMO Weight Notifications Setup

## 📖 **Read Files in This Order:**

### **1. First Read This → `READ_ME_FIRST.md` (this file)**
Quick overview of what to do

### **2. Then Read → `CPANEL_README.md`** 
Simple setup commands for your hosting type

### **3. If You Need Details → `cpanel_deployment_guide.md`**
Complete technical guide (only if you have problems)

---

## 🎯 **Quick Setup (Most People Start Here):**

### **Option A: Shared Hosting (95% of cPanel users)**
1. **Upload all files** to your cPanel server at: `/home/fammkoqw/public_html/fammo/`

2. **Add ONE cron job** in cPanel → Cron Jobs:
   ```
   0 */6 * * * /home/fammkoqw/public_html/fammo/.venv/bin/python /home/fammkoqw/public_html/fammo/cron_weight_notifications.py
   ```

3. **Test it works:**
   ```bash
   cd /home/fammkoqw/public_html/fammo
   python cron_weight_notifications.py
   ```

4. **Done!** Weight notifications will check every 6 hours automatically.

### **Option B: VPS/Cloud Server (Advanced users)**
1. **Upload files** to your server
2. **Run:** `./fammo_services.sh start`
3. **Done!** Services run automatically.

---

## 📱 **What This Does:**
- **Checks pets daily** for missing/overdue weight updates
- **Sends notifications** to pet owners at `/en/notifications/`
- **Smart scheduling** based on pet age and species  
- **Auto-resolves** when users add weight records

---

## 🆘 **Need Help?**
1. **Problems?** → Read `CPANEL_README.md`
2. **Technical details?** → Read `cpanel_deployment_guide.md`  
3. **Still stuck?** → Check the logs in `/home/fammkoqw/public_html/fammo/logs/`

## 📁 **File Reference:**
| File | What It Does |
|------|-------------|
| **`READ_ME_FIRST.md`** | ← **YOU ARE HERE** - Start here |
| `CPANEL_README.md` | Quick setup commands |
| `cron_weight_notifications.py` | The main script (already configured) |
| `fammo_services.sh` | VPS service management |
| `cpanel_deployment_guide.md` | Technical documentation |

---

**🎉 For 95% of users: Just add the cron job above and you're done!**