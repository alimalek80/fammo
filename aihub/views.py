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
        "You are a professional pet nutritionist. Based on the pet profile below, generate a detailed one-day meal plan.\n\n"
        "Format the response using structured Markdown, with clear section titles, bullet points, and tables.\n"
        "Use relevant emoji at the start of each section and meal (e.g., 🍽️ for meals, 🐾 for recommendations, 🥦 for vegetables).\n"
        "Be helpful, clear, and visually engaging — but do not overuse emojis.\n\n"
        "Structure:\n"
        "🍲 **1. Home-Cooked Meals**\n"
        "- Provide plans for **🍳 Breakfast**, **🍗 Lunch**, and **🐟 Dinner**.\n"
        "- Each meal should include:\n"
        "  - **Meal Title**\n"
        "  - **Ingredients** (list with emoji where appropriate)\n"
        "  - **Preparation** steps\n"
        "  - **Nutrition Table**: with columns (Calories, Protein, Fat, Carbs, Fiber)\n\n"
        "🥫 **2. Ready-Made Food Options**\n"
        "- Suggest non-branded wet/dry food with estimated nutrition in table format\n"
        "- Use emoji like 🥫 for wet food and 🐶 for dry food\n\n"
        "✅ **3. Suitability Explanation**\n"
        "- Bullet points explaining why this plan fits the pet’s breed, age, activity, or health\n"
        "- Use icons like ❤️, ⚠️, 💡 if relevant\n\n"
        f"Pet Profile:\n{pet_profile}"
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
        "You are a professional pet health consultant. Based on the pet profile below, generate a health insight report "
        "in structured Markdown format with appropriate section headers, bullet points, and relevant emojis for clarity and friendliness.\n\n"
        "Please use the following sections:\n\n"
        "🩺 **Health Summary**\n"
        "- A short paragraph summarizing the pet’s current health status\n\n"
        "🧬 **Breed-Specific Health Risks**\n"
        "- Bullet list of common genetic or breed-specific issues (if any)\n\n"
        "⚖️ **Weight and Diet Overview**\n"
        "- A paragraph about the pet’s current weight, appetite, and dietary suggestions\n\n"
        "🍽️ **Feeding Recommendations**\n"
        "- 2–3 bullet points offering practical, concise feeding tips\n\n"
        "🏃 **Activity Recommendations**\n"
        "- A short paragraph encouraging proper activity level or play for this pet\n\n"
        "⚠️ **Critical Alerts**\n"
        "- If there are urgent risks (e.g., obesity, kidney disease), list them\n"
        "- If none, write: `No critical issues detected ✅`\n\n"
        "Be informative but concise. Make it easy to scan. Use bullet points and emojis only to enhance clarity — do not overuse them.\n\n"
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