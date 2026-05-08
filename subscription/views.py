from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings as django_settings
from subscription.models import SubscriptionPlan, SubscriptionTransaction


def subscription_plans_view(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to view this page")
        return redirect('login')

    plans = SubscriptionPlan.objects.all().order_by('price_eur')

    if request.method == "POST":
        selected_plan_id = request.POST.get("plan_id")
        if selected_plan_id:
            plan = get_object_or_404(SubscriptionPlan, id=selected_plan_id)
            # Paid plans go through the checkout flow
            if plan.price_eur > 0:
                return redirect('subscription_checkout', plan_id=plan.id)
            # Free plan: activate directly
            profile = request.user.profile
            profile.subscription_plan = plan
            profile.save()
            messages.success(request, f"You are now on the {plan.get_name_display()} plan.")
            return redirect("pet:my_pets")

    return render(request, "subscription/plan_list.html", {
        "plans": plans,
        "current_plan": request.user.profile.subscription_plan,
    })


@login_required
def checkout_view(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if request.method == "POST":
        card_number = request.POST.get("card_number", "").replace(" ", "").replace("-", "")
        card_last4 = card_number[-4:] if len(card_number) >= 4 else "0000"

        # Activate the plan immediately (demo mode)
        profile = request.user.profile
        profile.subscription_plan = plan
        profile.save()

        transaction = SubscriptionTransaction.objects.create(
            user=request.user,
            plan=plan,
            amount=plan.price_eur,
            status='demo',
            card_last4=card_last4,
        )

        # Notify admin
        try:
            send_mail(
                subject=f"[FAMO Demo] New Subscription — {plan.get_name_display()}",
                message=(
                    f"A user subscribed in demo mode.\n\n"
                    f"User:   {request.user.email}\n"
                    f"Plan:   {plan.get_name_display()}\n"
                    f"Amount: €{plan.price_eur}/mo\n"
                    f"Status: Demo (no real payment charged)\n"
                    f"Tx ID:  #{transaction.id}\n\n"
                    f"The plan has been activated automatically."
                ),
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[django_settings.EMAIL_HOST_USER],
                fail_silently=True,
            )
        except Exception:
            pass

        # Send invoice to the user
        try:
            profile = request.user.profile
            user_name = f"{profile.first_name} {profile.last_name}".strip() or request.user.email
            send_mail(
                subject=f"Your FAMO {plan.get_name_display()} Plan — Invoice #{transaction.id}",
                message=(
                    f"Hi {user_name},\n\n"
                    f"Thank you for subscribing to FAMO! Your plan is now active.\n\n"
                    f"──────────────────────────────\n"
                    f"  INVOICE #{transaction.id}\n"
                    f"──────────────────────────────\n"
                    f"  Plan:    {plan.get_name_display()}\n"
                    f"  Amount:  €{plan.price_eur}/month\n"
                    f"  Card:    •••• •••• •••• {transaction.card_last4}\n"
                    f"  Date:    {transaction.created_at.strftime('%B %d, %Y')}\n"
                    f"  Status:  Demo (no real charge)\n"
                    f"──────────────────────────────\n\n"
                    f"We are currently in Beta — no payment has been charged.\n"
                    f"You can enjoy all premium features right now.\n"
                    f"We will notify you before real billing begins.\n\n"
                    f"If you have any questions, just reply to this email.\n\n"
                    f"The FAMO Team"
                ),
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, f"You are now on the {plan.get_name_display()} plan!")
        return redirect("subscription_success", transaction_id=transaction.id)

    # Pre-fill demo card details so users see the full checkout experience
    profile = request.user.profile
    demo_name = f"{profile.first_name} {profile.last_name}".strip() or request.user.email
    return render(request, "subscription/checkout.html", {
        "plan": plan,
        "demo_card": "4242 4242 4242 4242",
        "demo_expiry": "12/28",
        "demo_cvc": "123",
        "demo_name": demo_name,
    })


@login_required
def payment_success_view(request, transaction_id):
    transaction = get_object_or_404(
        SubscriptionTransaction, id=transaction_id, user=request.user
    )
    return render(request, "subscription/success.html", {"transaction": transaction})


@login_required
def billing_view(request):
    transactions = SubscriptionTransaction.objects.filter(
        user=request.user
    ).select_related('plan').order_by('-created_at')

    current_plan = request.user.profile.subscription_plan
    all_plans = SubscriptionPlan.objects.all().order_by('price_eur')

    return render(request, "subscription/billing.html", {
        "transactions": transactions,
        "current_plan": current_plan,
        "all_plans": all_plans,
    })
