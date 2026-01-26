# FAMMO Backend Git Synchronization Guide

This guide helps you maintain synchronization between your local development environment and cPanel production environment.

## Environment Setup

### Local Development
- Uses SQLite database by default
- Static files served at `/static/` and `/media/`
- All apps enabled including development tools

### cPanel Production
- Uses MySQL database
- Static files served at `fammo/static/` and `/fammo/media/`
- Production-optimized settings

## Environment Variables

Copy `.env.example` to `.env` and configure:

### For Local Development:
```bash
DEBUG=True
IS_CPANEL=False
USE_MYSQL=False
NPM_BIN_PATH=npm
NODE_BIN_PATH=node
```

### For cPanel Production:
```bash
DEBUG=False
IS_CPANEL=True
USE_MYSQL=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST_LOCAL=localhost
NPM_BIN_PATH=/home/fammkoqw/nodevenv/nodeapp/20/bin/npm
NODE_BIN_PATH=/home/fammkoqw/nodevenv/nodeapp/20/bin/node
```

## Git Workflow

### 1. Synchronize Local with cPanel (First Time)

```bash
# Run the deployment script
./deploy.sh sync

# Check everything is working
./deploy.sh check
```

### 2. Regular Development Workflow

```bash
# Make your changes locally
git add .
git commit -m "Your commit message"
git push origin main

# On cPanel server:
git pull origin main

# Apply migrations if needed
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput
```

### 3. Handling Migration Conflicts

If you encounter migration conflicts:

```bash
# Local: Create backup
./deploy.sh backup

# Reset migrations (CAREFUL - this will lose migration history)
rm */migrations/0*.py
python manage.py makemigrations
python manage.py migrate

# Or merge migrations manually
python manage.py makemigrations --merge
```

## Key Files Synchronized

- `famo/settings.py` - Environment-aware settings
- All `*/migrations/*.py` - Database migration files
- `requirements.txt` - Python dependencies
- Static files and templates

## Troubleshooting

### Migration Issues
```bash
# Check migration status
python manage.py showmigrations

# Reset database (LOCAL ONLY!)
rm db.sqlite3
python manage.py migrate
```

### Environment Detection Not Working
Check your `.env` file has correct `IS_CPANEL` setting.

### Static Files Not Loading
Run `python manage.py collectstatic` after deployment.

## Pre-deployment Checklist

- [ ] All changes committed and pushed to Git
- [ ] `.env` file configured correctly for target environment
- [ ] Migration files are synchronized
- [ ] `python manage.py check` passes without errors
- [ ] Static files collected if needed

## Important Notes

1. **Never** commit `.env` files to Git
2. **Always** test locally before pushing to production
3. **Backup** migrations before making changes
4. **Use** the deployment script for synchronization
5. **Keep** both repositories in sync by using the same Git remote