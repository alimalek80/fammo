from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .ai_service import pet_answer
from pet.models import Pet

@require_http_methods(["GET", "POST"])
def chat(request):
    # reset chat if ?new=1
    if request.GET.get("new") == "1":
        request.session["history"] = []
        request.session.modified = True
        return redirect("chat")
    
    # keep a tiny convo history in session
    history = request.session.get("history", [])

    # Personalization context
    user_first = None
    pet_profiles = None
    primary_pet = None

    if request.user.is_authenticated:
        # best-effort first name (prefer Profile.first_name from custom user app)
        profile = getattr(request.user, "profile", None)
        if profile and getattr(profile, "first_name", None):
            user_first = (profile.first_name or "").strip()
        else:
            # fallback to username or email localpart
            username_like = getattr(request.user, "username", None) or getattr(request.user, "email", "")
            user_first = (username_like or "").split("@")[0]
        # fetch user's pets
        pets_qs = Pet.objects.filter(user=request.user).select_related(
            "pet_type", "breed", "gender", "age_category", "body_type", "activity_level", "food_feeling", "food_importance", "treat_frequency"
        ).prefetch_related("food_types", "food_allergies", "health_issues")
        pets = list(pets_qs)
        if pets:
            primary_pet = pets[0]
            # build profiles string (for multiple pets include all)
            parts = []
            for idx, p in enumerate(pets, start=1):
                parts.append(f"Pet {idx}:\n" + p.get_full_profile_for_ai())
            pet_profiles = "\n\n".join(parts)

    if request.method == "POST":
        user_msg = (request.POST.get("message") or "").strip()
        if not user_msg:
            return render(request, "chat/chat.html", {
                "history": history,
                "error": "Please type a question.",
                "user_first": user_first,
                "primary_pet": primary_pet,
            })
        
        # Append user message
        history.append({"role": "user", "text": user_msg})
        
        # Check if this is the first user message (history was empty before appending)
        is_first_message = len(history) == 1
        
        # real AI answer with personalization context
        bot_reply = pet_answer(user_msg, user_name=user_first, pet_profiles=pet_profiles, is_first_message=is_first_message)
        
        history.append({"role": "bot", "text": bot_reply})

        # save back to session
        request.session["history"] = history
        request.session.modified = True

        return redirect("chat")
    
    # Personalized greeting (client shows this when no history exists)
    greeting = None
    if not history:
        if user_first and primary_pet:
            greeting = f"Hi {user_first}! I'm here to help you about {primary_pet.name}. Do you have any question?"
        elif user_first:
            greeting = f"Hi {user_first}! I'm here to help you with your dog or cat. Do you have any question?"
        else:
            greeting = None  # template will fallback to default text

    return render(request, "chat/chat.html", {
        "history": history,
        "user_first": user_first,
        "primary_pet": primary_pet,
        "greeting": greeting,
    })