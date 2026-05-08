from django.urls import path
from .views import subscription_plans_view, checkout_view, payment_success_view, billing_view

urlpatterns = [
    path('plans/', subscription_plans_view, name='subscription_plans'),
    path('checkout/<int:plan_id>/', checkout_view, name='subscription_checkout'),
    path('success/<int:transaction_id>/', payment_success_view, name='subscription_success'),
    path('billing/', billing_view, name='subscription_billing'),
]
