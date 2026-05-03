"""
Email Preview — staff-only views for inspecting all Fammo email templates.
Accessible at /dev/emails/ to any logged-in staff/admin user.
"""

from datetime import date, time, datetime
from types import SimpleNamespace

from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string


# ---------------------------------------------------------------------------
# Mock data helpers
# ---------------------------------------------------------------------------

def _mock_data():
    """Return a dict of SimpleNamespace objects that mimic real model instances."""

    user = SimpleNamespace(
        email="john.doe@example.com",
        profile=SimpleNamespace(first_name="John", last_name="Doe"),
    )

    clinic = SimpleNamespace(
        id=1,
        name="Happy Paws Veterinary Clinic",
        email="clinic@happypaws.com",
        city="Melbourne",
        address="123 Pet Street, Melbourne VIC 3000",
        phone="+61 3 9999 1234",
        website="https://happypaws.com",
        specializations="General Practice, Surgery",
        bio="We provide expert, compassionate care for your beloved pets.",
        slug="happy-paws-veterinary-clinic",
        email_confirmed=True,
        admin_approved=False,
        owner=SimpleNamespace(
            email="owner@happypaws.com",
            get_full_name=lambda: "Dr. Sarah Smith",
            username="sarahsmith",
        ),
        created_at=datetime(2025, 5, 1, 10, 30),
        working_hours=None,
    )

    pet = SimpleNamespace(
        name="Max",
        pet_type=SimpleNamespace(name="Dog"),
        breed=SimpleNamespace(name="Golden Retriever"),
    )

    appointment = SimpleNamespace(
        reference_code="FAM-2025-001",
        appointment_date=date(2025, 6, 15),
        appointment_time=time(14, 30),
        duration_minutes=30,
        notes="Regular annual checkup",
        cancellation_reason="Vet unavailable due to an emergency",
        get_status_display=lambda: "Confirmed",
    )

    return {
        "user": user,
        "clinic": clinic,
        "pet": pet,
        "appointment": appointment,
    }


# ---------------------------------------------------------------------------
# Email registry
# ---------------------------------------------------------------------------

EMAILS = {
    "user-activation": {
        "title": "User Account Activation",
        "subject": "Activate your FAMO account",
        "description": "Sent to new users after they register. Contains the email verification link.",
        "recipient": "New user (pet owner)",
        "template": "userapp/account_activation_email.html",
        "context_fn": lambda d: {
            "user": d["user"],
            "domain": "fammo.ai",
            "uid": "Mw",
            "token": "sample-token-abc123",
            "from_app": False,
        },
    },
    "clinic-email-confirmation": {
        "title": "Clinic Email Confirmation",
        "subject": "Confirm Your Clinic Email - FAMMO",
        "description": "Sent to clinic owners when they register. They must click to confirm their email before admin review.",
        "recipient": "Clinic owner",
        "template": "vets/emails/clinic_email_confirmation.html",
        "context_fn": lambda d: {
            "clinic": d["clinic"],
            "confirmation_url": "https://fammo.ai/vets/confirm-email/1/sample-token-xyz/",
            "site_name": "FAMMO",
            "domain": "fammo.ai",
        },
    },
    "admin-clinic-notification": {
        "title": "New Clinic Pending Admin Approval",
        "subject": "New Clinic Pending Approval - Happy Paws Veterinary Clinic",
        "description": "Sent to Fammo admins after a clinic confirms their email. Prompts admin to review and approve the listing.",
        "recipient": "Fammo admin team",
        "template": "vets/emails/admin_clinic_notification.html",
        "context_fn": lambda d: {
            "clinic": d["clinic"],
            "admin_url": "https://fammo.ai/admin/vets/clinic/1/change/",
            "site_name": "FAMMO",
            "domain": "fammo.ai",
        },
    },
    "appointment-new-clinic": {
        "title": "New Appointment Booking (→ Clinic)",
        "subject": "New Appointment: Max — FAM-2025-001",
        "description": "Sent to the clinic when a pet owner books an appointment.",
        "recipient": "Clinic",
        "template": "vets/emails/appointment_new_notification.html",
        "context_fn": lambda d: {
            "clinic": d["clinic"],
            "appointment": d["appointment"],
            "pet": d["pet"],
            "user_name": "John Doe",
            "user_email": "john.doe@example.com",
            "user_phone": "+61 400 123 456",
            "reason": "Annual vaccination and general health checkup",
            "site_name": "FAMMO",
        },
    },
    "appointment-cancelled-clinic": {
        "title": "Appointment Cancelled by User (→ Clinic)",
        "subject": "Appointment Cancelled - Max (FAM-2025-001)",
        "description": "Sent to the clinic when a pet owner cancels their appointment.",
        "recipient": "Clinic",
        "template": "vets/emails/appointment_cancelled_notification.html",
        "context_fn": lambda d: {
            "clinic": d["clinic"],
            "appointment": d["appointment"],
            "pet": d["pet"],
            "user_name": "John Doe",
            "cancellation_reason": "Change of plans — will reschedule next week.",
            "site_name": "FAMMO",
        },
    },
    "appointment-confirmed-user": {
        "title": "Appointment Confirmed (→ User)",
        "subject": "Appointment Confirmed - Max at Happy Paws Veterinary Clinic",
        "description": "Sent to the pet owner when the clinic confirms their appointment.",
        "recipient": "Pet owner",
        "template": "vets/emails/appointment_confirmed_user.html",
        "context_fn": lambda d: {
            "clinic": d["clinic"],
            "appointment": d["appointment"],
            "pet": d["pet"],
            "user_name": "John",
            "site_name": "FAMMO",
        },
    },
    "appointment-cancelled-by-clinic": {
        "title": "Appointment Cancelled by Clinic (→ User)",
        "subject": "Appointment Cancelled by Clinic - Max",
        "description": "Sent to the pet owner when the clinic cancels their appointment.",
        "recipient": "Pet owner",
        "template": "vets/emails/appointment_cancelled_by_clinic_user.html",
        "context_fn": lambda d: {
            "clinic": d["clinic"],
            "appointment": d["appointment"],
            "pet": d["pet"],
            "user_name": "John",
            "site_name": "FAMMO",
        },
    },
    "appointment-reminder": {
        "title": "Appointment Reminder (→ User)",
        "subject": "Reminder: Appointment Tomorrow - Max at Happy Paws Veterinary Clinic",
        "description": "Sent to the pet owner ~24 hours before their scheduled appointment.",
        "recipient": "Pet owner",
        "template": "vets/emails/appointment_reminder_user.html",
        "context_fn": lambda d: {
            "clinic": d["clinic"],
            "appointment": d["appointment"],
            "pet": d["pet"],
            "user_name": "John",
            "site_name": "FAMMO",
        },
    },
    "appointment-status-update": {
        "title": "Appointment Status Update (→ User)",
        "subject": "Appointment Update - Max",
        "description": "Sent to the pet owner when an appointment status changes (e.g. completed).",
        "recipient": "Pet owner",
        "template": "vets/emails/appointment_status_update_user.html",
        "context_fn": lambda d: {
            "clinic": d["clinic"],
            "appointment": d["appointment"],
            "pet": d["pet"],
            "user_name": "John",
            "status_display": "Confirmed",
            "site_name": "FAMMO",
        },
    },
}

# Group emails for the index page
EMAIL_GROUPS = [
    {
        "name": "User Emails",
        "color": "indigo",
        "keys": ["user-activation"],
    },
    {
        "name": "Clinic Emails",
        "color": "green",
        "keys": ["clinic-email-confirmation", "admin-clinic-notification"],
    },
    {
        "name": "Appointment Emails — to Clinic",
        "color": "blue",
        "keys": ["appointment-new-clinic", "appointment-cancelled-clinic"],
    },
    {
        "name": "Appointment Emails — to User",
        "color": "purple",
        "keys": [
            "appointment-confirmed-user",
            "appointment-cancelled-by-clinic",
            "appointment-reminder",
            "appointment-status-update",
        ],
    },
]


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

@staff_member_required
def email_preview_index(request):
    """Index listing all previewable emails — staff only."""
    groups = []
    for group in EMAIL_GROUPS:
        items = []
        for key in group["keys"]:
            cfg = EMAILS.get(key)
            if cfg:
                items.append({"key": key, **cfg})
        groups.append({**group, "items": items})

    return render(request, "core/email_preview_index.html", {"groups": groups})


@staff_member_required
def email_preview_detail(request, email_key):
    """Render a single email template with sample data — staff only."""
    cfg = EMAILS.get(email_key)
    if not cfg:
        raise Http404

    mock = _mock_data()
    context = cfg["context_fn"](mock)
    html = render_to_string(cfg["template"], context)
    return HttpResponse(html)
