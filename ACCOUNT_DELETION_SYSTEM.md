# Account Deletion System - Implementation Guide

## Overview
Complete account deletion request system with admin approval, countdown timer, and automatic processing.

## Features Implemented

### 1. User Request Flow
- Users can request account deletion from their profile
- Shows what data will be deleted (pets, clinic, AI data, etc.)
- Requires confirmation checkbox
- Optional reason field

### 2. Admin Approval System
- Admins receive email notifications
- Admin panel to review requests
- One-click approval button
- Sets 15-day countdown after approval
- Email sent to user upon approval

### 3. Dashboard Warning Banner
- Shows pending/approved deletion requests
- Displays countdown (e.g., "9 days remaining")
- Cancel button available until deletion date
- Warning that account cannot be recovered

### 4. Automatic Deletion
- Management command: `process_account_deletions`
- Deletes users whose 15-day period has expired
- Deletes all related data:
  - User account & profile
  - Pet profiles
  - Clinic information
  - AI recommendations & health reports
  - Uploaded media
- Sends final confirmation email
- Marks request as completed

### 5. Public Policy Page
- URL: https://fammo.ai/delete-account/
- Explains deletion process
- Lists what data is deleted/retained
- Contact information
- FAQs

## Setup Instructions

### Step 1: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Set Up Cron Job (Production)
Add to crontab to run daily:
```bash
0 2 * * * cd /path/to/fammo && python manage.py process_account_deletions
```

Or use Django-cron or Celery Beat for scheduled tasks.

### Step 3: Test the System

#### Test Request Flow:
1. Log in as a regular user
2. Go to Profile Settings
3. Click "Request Account Deletion"
4. Fill form and submit
5. Check dashboard for warning banner

#### Test Admin Approval:
1. Log in to admin panel
2. Go to Account Deletion Requests
3. Click "Approve" on pending request
4. User receives email with 15-day countdown

#### Test Cancellation:
1. Log in as user with pending request
2. Dashboard shows warning banner
3. Click "Cancel Deletion Request"
4. Request status changes to "Cancelled"

#### Test Automatic Deletion:
```bash
# Manually trigger (for testing)
python manage.py process_account_deletions

# Or wait for scheduled time
```

## URLs Added
- `/users/request-deletion/` - Request form
- `/users/cancel-deletion/` - Cancel request
- `/delete-account/` - Public policy page (no language prefix)
- `/users/delete-account/` - Policy page (with language prefix)

## Models
- `AccountDeletionRequest` - Tracks deletion requests
  - Status: pending, approved, cancelled, completed
  - Scheduled deletion date
  - Days until deletion counter
  - Tracks pets/clinic count

## Admin Features
- List view with status colors
- Days remaining countdown (red for urgent)
- One-click approval
- Admin notes field
- Search by email

## Email Notifications
1. **Admin notification** - When user requests deletion
2. **User approval email** - When admin approves (15-day warning)
3. **Final confirmation** - After account is deleted

## Security Notes
- Users cannot log in once deletion is completed
- Email becomes available for new registrations after deletion
- All data is permanently removed (no soft delete)
- Backup data removed within 90 days (as stated in policy)

## Monitoring
- Admin dashboard shows all requests
- Status tracking (pending/approved/completed)
- Completion timestamps
- Failed deletion tracking

## Future Enhancements
- [ ] Add automated reminders (3 days, 1 day before deletion)
- [ ] Export user data before deletion (GDPR compliance)
- [ ] Admin bulk approval
- [ ] Restore option within 24 hours
- [ ] Anonymize instead of delete (for analytics)
