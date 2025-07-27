import openai
from openai import OpenAI
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from pet.models import Pet
from .models import AIRecommendation, RecommendationType, AIHealthReport
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from datetime import datetime, timedelta
from django.utils.timezone import now
from subscription.models import AIUsage, first_day_of_current_month
from django.utils.translation import gettext_lazy as _


openai.api_key = settings.OPENAI_API_KEY

def generate_meal_recommendation(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, user=request.user)

    # Limit: 3 per user per month
    start_of_month = datetime(now().year, now().month, 1)
    used_count = AIRecommendation.objects.filter(
        pet__user=request.user,
        type=RecommendationType.MEAL,
        created_at__gte=start_of_month
    ).count()

    # Get the user's assigned plan from profile
    user_profile = request.user.profile
    meal_limit = user_profile.subscription_plan.monthly_meal_limit if user_profile.subscription_plan else 3

    if not request.user.is_superuser and used_count >= meal_limit:
        return render(request, 'aihub/limit_reached.html', {
            'message': _("You’ve reached your monthly limit of %(limit)s AI meal suggestions.") % {"limit": meal_limit}
        })

    pet_profile = pet.get_full_profile_for_ai()
    prompt = (
        "You are a professional pet nutritionist. Based on the following pet profile, "
        "suggest a balanced daily meal plan for one day. "
        "Please use this format:\n\n"
        "1. Home-cooked meals:\n"
        "   - For each meal (breakfast, lunch, dinner), specify:\n"
        "     • The recipe (ingredients and how to cook it, step by step)\n"
        "     • The nutrition values (calories, protein, fat, carbs, fiber, etc) for each meal\n"
        "2. Ready-made foods:\n"
        "   - Suggest suitable wet and/or dry foods available in the market\n"
        "   - Write their estimated nutrition values\n"
        "3. Separate home-cooked and ready-made foods clearly.\n"
        "4. Ensure the plan is suitable for the pet's age, weight, breed, and health conditions.\n"
        "5. Please use clear headings for each section and use bullet points or tables for nutrition values if possible."
        "6. for ready made food please No Brand food suggest.\n"
        "7. Explain why this plan is suitable for this pet.\n\n"
        "Pet Profile:\n"
        f"{pet_profile}"
    )

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    chat_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    result = chat_response.choices[0].message.content

    recommendation = AIRecommendation.objects.create(
        pet=pet,
        type=RecommendationType.MEAL,
        content=result
    )

    # Only track usage for normal users
    if not request.user.is_superuser:
        from subscription.models import AIUsage, first_day_of_current_month

        usage, created = AIUsage.objects.get_or_create(
            user=request.user,
            month=first_day_of_current_month()
        )
        usage.meal_used += 1
        usage.save()

    return render(request, 'aihub/meal_result.html', {
        'recommendation': recommendation,
        'pet': pet
    })

def generate_health_report(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id, user=request.user)

    start_of_month = datetime(now().year, now().month, 1)
    used_count = AIHealthReport.objects.filter(
        pet__user=request.user,
        created_at__gte=start_of_month
    ).count()

    user_profile = request.user.profile
    health_limit = user_profile.subscription_plan.monthly_health_limit if user_profile.subscription_plan else 1

    if not request.user.is_superuser and used_count >= health_limit:
        return render(request, 'aihub/limit_reached.html', {
            'message': _("You’ve reached your monthly limit of %(limit)s AI health reports.") % {"limit": health_limit}
        })

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    pet_profile = pet.get_full_profile_for_ai()
    prompt = (
        "You are a professional pet health consultant. Based on the following pet profile, "
        "provide a short health insight report. Mention risks, diet, or activity suggestions. "
        "Highlight any critical health issues.\n\n"
        f"Pet Profile:\n{pet_profile}"
    )

    chat_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    result = chat_response.choices[0].message.content

    # Split into summary + suggestions if needed
    report = AIHealthReport.objects.create(
        pet=pet,
        summary=result
    )

    if not request.user.is_superuser:
        usage, created = AIUsage.objects.get_or_create(
            user=request.user,
            month=first_day_of_current_month()
        )
        usage.health_used += 1
        usage.save()

    return render(request, 'aihub/health_report.html', {
        'report': report,
        'pet': pet
    })

@method_decorator(login_required, name='dispatch')
class AIHistoryView(TemplateView):
    template_name = 'aihub/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_pets = self.request.user.pets.all()
        context['user_pets'] = user_pets  # <-- Add this line
        context['recommendations'] = AIRecommendation.objects.filter(pet__in=user_pets).order_by('-created_at')
        context['reports'] = AIHealthReport.objects.filter(pet__in=user_pets).order_by('-created_at')
        return context