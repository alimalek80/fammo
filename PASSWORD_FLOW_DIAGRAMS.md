# Password Management Flow - Complete Visual Guide

## The Three Password Operations

### 1️⃣ CHANGE PASSWORD (Logged In User)

```
┌─ User is logged in ─┐
│   (has JWT token)   │
└─────────┬───────────┘
          │
          ↓
    ┌─────────────────────────────────┐
    │ Change Password Screen          │
    ├─────────────────────────────────┤
    │ Old Password: [__________]      │
    │ New Password: [__________]      │
    │ Confirm:     [__________]       │
    │                                 │
    │ [Change Password] Button        │
    └──────────────┬──────────────────┘
                   │
                   ↓
    POST /api/v1/auth/change-password/
    Headers: Authorization: Bearer {token}
    Body: {
      old_password: "...",
      new_password: "...",
      new_password_confirm: "..."
    }
                   │
        ┌──────────┴──────────┐
        │                     │
        ↓                     ↓
    ✅ SUCCESS          ❌ ERROR
    {success: true}     {error: "..."}
        │                     │
        ↓                     ↓
    Show "Changed!"     Show error message
    User logged in
```

---

### 2️⃣ FORGOT PASSWORD (Anonymous - Email)

```
┌─ User forgot password ─┐
│   (not logged in)      │
└───────────┬────────────┘
            │
            ↓
    ┌──────────────────────────────┐
    │ Forgot Password Screen       │
    ├──────────────────────────────┤
    │ Email: [user@example.com]    │
    │                              │
    │ [Send Reset Link] Button     │
    └──────────┬───────────────────┘
               │
               ↓
    POST /api/v1/auth/forgot-password/
    Body: {email: "user@example.com"}
               │
               ↓
    ✅ Email Sent (always returns success for security)
               │
               ↓
    ┌──────────────────────────────────────┐
    │ Django generates:                    │
    │ - uid: base64 encoded user ID        │
    │ - token: secure random token        │
    │ - link: /reset-password/{uid}/{token}│
    └──────────┬───────────────────────────┘
               │
               ↓
    📧 Email Received by User:
    ┌────────────────────────────────────────┐
    │ Subject: Password Reset Request        │
    ├────────────────────────────────────────┤
    │ Click to reset password:               │
    │ https://fammo.ai/reset-password/       │
    │ MQ/d0n3rz-f64b0ee4712b9d209c6dcec...  │
    │                                        │
    │ [Click Link]                           │
    └────────┬───────────────────────────────┘
             │
             ↓
```

---

### 3️⃣ RESET PASSWORD (Via Email Link)

```
┌─ User clicks link from email ─┐
│ /reset-password/{uid}/{token}/ │
└───────────┬─────────────────────┘
            │
            ↓ (Browser opens)
    GET /reset-password/{uid}/{token}/
            │
            ↓
    ┌─────────────────────────────────┐
    │ Django validates:               │
    │ ✓ Decode uid → get user         │
    │ ✓ Check token (not expired?)    │
    └──────────┬──────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ↓             ↓
    ✅ VALID      ❌ INVALID
        │             │
        ↓             ↓
    ┌────────────┐  ┌─────────────────┐
    │ Show Form  │  │ Error Page      │
    └─────┬──────┘  ├─────────────────┤
          │         │ Invalid/Expired │
          ↓         │ Request New Link│
    ┌──────────────────────────┐ │
    │ 🔐 Reset Password        │ └─→ [Redirect to Login]
    │ Account: user@exam.com   │
    ├──────────────────────────┤
    │ New Password: [______]   │
    │ Confirm:     [______]    │
    │                          │
    │ [Reset Password] Button  │
    └──────┬───────────────────┘
           │
      POST (same URL)
           │
           ↓ (User submits)
    ┌────────────────────────────┐
    │ Validate Password:         │
    │ ✓ Not empty                │
    │ ✓ Min 8 characters         │
    │ ✓ Passwords match          │
    └──────────┬─────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ↓             ↓
    ✅ VALID      ❌ INVALID
        │             │
        ↓             ↓
    Hash & Save   Show Error
    Password      (stay on form)
        │             │
        ↓             ↓
    ✅ Success        User fixes
    Message          and retries
        │
        ↓
    ┌─────────────────────────────┐
    │ ✅ Password Reset Success!  │
    │ You can now log in          │
    │ [Go to Login]               │
    └──────────┬──────────────────┘
               │
               ↓ (after 3 seconds)
    Redirect to Login Page
               │
               ↓
    ┌──────────────────────────────┐
    │ Login Screen                 │
    ├──────────────────────────────┤
    │ Email:    [user@exam.com]    │
    │ Password: [NewPassword456]   │
    │                              │
    │ [Login] Button               │
    └──────────┬───────────────────┘
               │
               ↓
    POST /api/v1/auth/token/
    Body: {email: "...", password: "..."}
               │
               ↓
    ✅ JWT Token Returned
    {access: "...", refresh: "..."}
               │
               ↓
    🎉 Logged In! Access App
```

---

## Decision Tree

```
                    User wants to reset password
                              │
                              ↓
                ┌─────────────────────────┐
                │ Are they logged in?     │
                └────────┬────────────────┘
                         │
           ┌─────────────┴─────────────┐
           │                           │
          YES                         NO
           │                           │
           ↓                           ↓
    Use:                      ┌──────────────────┐
    /auth/change-password/    │ Do they have     │
    (need old password)       │ reset email link?│
                              └────┬─────────────┘
                                   │
                          ┌────────┴────────┐
                          │                 │
                         YES               NO
                          │                 │
                          ↓                 ↓
                  Use:                Use:
                  /reset-password/    /auth/forgot-password/
                  {uid}/{token}/      (email only)
                  (from email)        ↓ Get email
                                      ↓ Click link
                                      ↓ See form above
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         PASSWORD SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  FLUTTER APP                    DJANGO BACKEND                  │
│  ──────────                     ──────────────                  │
│                                                                   │
│  ┌─────────────────────────┐    ┌──────────────────────────┐   │
│  │ Change Password Screen  │    │ POST /auth/change-pass/  │   │
│  │ Old: [___]   New: [___] │───→│ (validate old password)  │   │
│  │              [Change]   │    │ (hash new password)      │   │
│  └─────────────────────────┘    │ → Database.update()      │   │
│                                  └──────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────┐    ┌──────────────────────────┐   │
│  │ Forgot Password Screen  │    │ POST /auth/forgot-pass/  │   │
│  │ Email: [___]            │───→│ (generate token)         │   │
│  │ [Send Reset Link]       │    │ (send email)             │   │
│  └──────────┬──────────────┘    │ → Email Backend          │   │
│             │                    └──────────────────────────┘   │
│             │ User gets email                                    │
│             ↓ with link                                          │
│  ┌─────────────────────────┐    ┌──────────────────────────┐   │
│  │ Browser (Mobile)        │    │ GET /reset-password/.../ │   │
│  │ Shows reset form        │←───│ (validate token)         │   │
│  │ New: [___]  Confirm[___]│    │ (show form)              │   │
│  │ [Reset Password]        │───→│ POST /reset-password/    │   │
│  └─────────────────────────┘    │ (validate password)      │   │
│             ↓                    │ (hash & save)            │   │
│  ┌─────────────────────────┐    │ (show success)           │   │
│  │ Success → Login         │    └──────────────────────────┘   │
│  │ New password works! ✅  │                                    │
│  └─────────────────────────┘                                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security Features

```
PASSWORD RESET SECURITY CHECKS
═════════════════════════════════════════════════════════════════

✅ Token Validation
   - Token generated using Django's default_token_generator
   - Token includes user ID + timestamp + secret key
   - Signature verified on each use
   
✅ Time-Based Expiration
   - Default: 24 hours (configurable)
   - Older tokens automatically fail validation
   - No need to store expiry in database
   
✅ One-Time Use
   - Token is tied to specific user
   - Can't be used for different user
   - Can't be used after password changes
   
✅ Password Security
   - Min 8 characters enforced
   - Passwords hashed with PBKDF2 (Django default)
   - Salt included in hash
   
✅ CSRF Protection
   - All forms include CSRF token
   - POST requests validated
   
✅ Email Privacy
   - /forgot-password/ returns success even if email doesn't exist
   - Prevents account enumeration attacks
   
✅ HTTPS Required (Production)
   - All password operations over HTTPS
   - Tokens not logged in plain text
   - No sensitive data in URL (except token for retrieval)
```

---

## Status Flow

```
FORGOT PASSWORD STATUS FLOW
═════════════════════════════════════════════════════════════════

1. User requests reset
   Status: "Email Sent" ✅

2. User gets email
   Status: "Check your email" 📧

3. User clicks link
   Status: "Password Form" 📝

4. User submits password
   Status: "Processing..." ⏳

5. Password reset
   Status: "Success! Login now" ✅

6. User logs in
   Status: "Logged In" 🔓

7. User accesses app
   Status: "Using App" ✨


CHANGE PASSWORD STATUS FLOW
═════════════════════════════════════════════════════════════════

1. User clicks "Change Password"
   Status: "Open Form" 📝

2. User enters old password
   Status: "Validating..." ⏳

3. Password verified
   Status: "Valid! Continue" ✅

4. User enters new password
   Status: "Ready to submit" 📝

5. Form submitted
   Status: "Updating..." ⏳

6. Password updated
   Status: "Changed! ✅" 

7. Back in app
   Status: "Session continues" ✨
```

---

## Complete User Journey

```
         CHANGE PASSWORD JOURNEY
    ┌────────────────────────────────┐
    │ User logged in                 │
    │ Has valid JWT token            │
    └────────────┬────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────┐
    │ Open Settings/Account          │
    │ Tap "Change Password"          │
    └────────────┬────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────┐
    │ Enter Old Password             │
    │ Enter New Password (8+ chars)  │
    │ Confirm New Password           │
    │ Tap [Change Password]          │
    └────────────┬────────────────────┘
                 │
                 ↓ API Call
                 POST /auth/change-password/
                 │
        ┌────────┴────────┐
        │                 │
        ↓                 ↓
    ✅ Success          ❌ Error
        │                 │
        ↓                 ↓
    Show Success       Show Error
    "Changed!"         "Old password incorrect"
        │                 │
        ↓                 ↓
    Continue Using     Try Again
    App with new pwd


         FORGOT PASSWORD JOURNEY
    ┌────────────────────────────────┐
    │ User forgotten password        │
    │ Not logged in                  │
    └────────────┬────────────────────┘
                 │
                 ↓
    ┌────────────────────────────────┐
    │ Tap "Forgot Password?"         │
    │ Enter email address            │
    │ Tap [Send Reset Link]          │
    └────────────┬────────────────────┘
                 │
                 ↓ API Call
                 POST /auth/forgot-password/
                 │
                 ↓
    ✅ Success (always)
    "Check your email"
                 │
                 ↓
    User opens email app
    Finds password reset email
    Clicks link
                 │
                 ↓
    Browser opens
    GET /reset-password/{uid}/{token}/
                 │
                 ↓
    🔐 Password Reset Form appears
    "Reset Your Password"
                 │
                 ↓
    Enter new password
    Confirm new password
    Tap [Reset Password]
                 │
                 ↓
    ✅ Password Reset Success
    "You can now log in"
                 │
                 ↓
    Auto-redirect to Login
    User enters email + new password
    Gets JWT token
                 │
                 ↓
    🎉 Logged In!
    App access granted
```

---

## Error Handling Tree

```
CHANGE PASSWORD ERRORS
┌──────────────────────────────────────────┐
│ User submits change password form        │
└────────────┬─────────────────────────────┘
             │
       ┌─────┴─────┬──────────┬────────┬──────────┐
       │            │          │        │          │
       ↓            ↓          ↓        ↓          ↓
   ❌ Old Pass   ❌ New !=  ❌ Too   ❌ Same   ❌ No Auth
   Incorrect    Confirm   Short   as Old    (401)
       │            │        │        │         │
       ↓            ↓        ↓        ↓         ↓
   "Old pass   "Passwords "Min 8   "New pass "Invalid
    incorrect" don't match" chars"  is same" credentials"


FORGOT PASSWORD ERRORS
┌──────────────────────────────────────────┐
│ User submits forgot password form        │
└────────────┬─────────────────────────────┘
             │
             ↓
       ✅ Always returns success (security)
        No errors shown to user


RESET PASSWORD ERRORS (Web Form)
┌──────────────────────────────────────────┐
│ User clicks link from email              │
└────────────┬─────────────────────────────┘
             │
       ┌─────┴───────────┬──────────────────┐
       │                 │                  │
       ↓                 ↓                  ↓
   ✅ VALID TOKEN   ❌ INVALID TOKEN  ❌ EXPIRED
       │                 │              TOKEN
       ↓                 ↓                  ↓
   Show Form         Show Error        Show Error
   (ready to          "Invalid link"   "Link expired"
    reset)


   After form submission:
   ┌────────────────────────────────────┐
   │ Form validation errors             │
   └────┬─────────────┬────────────┬────┘
        │             │            │
        ↓             ↓            ↓
   ❌ Too Short  ❌ Not Match  ❌ Empty
       │             │            │
       ↓             ↓            ↓
   "Min 8 chars" "Passwords  "Fields
                 don't match" required"
```

All clear! The complete password management system is now working correctly. 🎉
