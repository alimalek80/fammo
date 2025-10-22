from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegistrationForm, ProfileForm, CustomLoginForm, SetPasswordForm
from .models import Profile
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from collections import Counter
from pet.models import Pet
from aihub.models import AIRecommendation, AIHealthReport
from aihub.utils import get_country_from_ip
import csv
from django.http import HttpResponse


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User inactive until email confirmation
            user.save()
            # Send activation email
            current_site = get_current_site(request)
            subject = "Activate your FAMO account"
            message = render_to_string('userapp/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, None, [user.email])
            messages.success(request, _("Registration successful. Please check your email to activate your account."))
            return redirect('login')
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = UserRegistrationForm()
    return render(request, 'userapp/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, _("You are already logged in."))
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, _("Login successful."))
            return redirect('dashboard')
        else:
            messages.error(request, _("Invalid login credentials."))
        form = CustomLoginForm(request, data=request.POST)
    else:
        form = CustomLoginForm()
    return render(request, 'userapp/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, _("You have been logged out."))
    return redirect('login')

@login_required
def update_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated successfully."))
            return redirect('dashboard')
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'userapp/update_profile.html', {'form': form})

@login_required
def dashboard_view(request):
    user = request.user
    pets = getattr(user, 'pets', None)
    if pets is not None:
        pets = user.pets.all()
    else:
        pets = []
    has_pets = pets.exists() if hasattr(pets, 'exists') else False
    messages.info(request, _("Welcome to your dashboard!"))
    return render(request, 'userapp/dashboard.html', {
        'has_pets': has_pets,
    })

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def users_admin_view(request):
    User = get_user_model()
    users = User.objects.all().prefetch_related('pets')
    
    return render(request, 'userapp/users_admin.html', {
        'users': users,
        
    })

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        # Check if there's pending pet data from wizard registration
        pending_pet_key = f'pending_pet_data_{user.pk}'
        pet_created = False
        pet_name = None
        
        if pending_pet_key in request.session:
            try:
                from pet.models import Pet, PetType, Gender, AgeCategory, Breed, FoodFeeling, FoodImportance, BodyType, ActivityLevel, TreatFrequency, FoodType, FoodAllergy, HealthIssue
                
                pet_data = request.session[pending_pet_key]
                pet_name = pet_data.get('name')
                
                # Check if pet was already created during registration (it should be)
                existing_pet = Pet.objects.filter(user=user, name=pet_name).first()
                if existing_pet:
                    pet_created = True
                    print(f"✅ Pet '{pet_name}' already exists for user {user.email}")  # Debug log
                else:
                    # Fallback: create pet if it doesn't exist for some reason
                    pet = Pet(user=user)
                    pet.name = pet_data.get('name')
                    
                    # Handle foreign key relationships
                    if pet_data.get('pet_type_id'):
                        pet.pet_type = PetType.objects.get(pk=pet_data['pet_type_id'])
                    if pet_data.get('gender_id'):
                        pet.gender = Gender.objects.get(pk=pet_data['gender_id'])
                    if pet_data.get('age_category_id'):
                        pet.age_category = AgeCategory.objects.get(pk=pet_data['age_category_id'])
                    if pet_data.get('breed_id'):
                        pet.breed = Breed.objects.get(pk=pet_data['breed_id'])
                    if pet_data.get('food_feeling_id'):
                        pet.food_feeling = FoodFeeling.objects.get(pk=pet_data['food_feeling_id'])
                    if pet_data.get('food_importance_id'):
                        pet.food_importance = FoodImportance.objects.get(pk=pet_data['food_importance_id'])
                    if pet_data.get('body_type_id'):
                        pet.body_type = BodyType.objects.get(pk=pet_data['body_type_id'])
                    if pet_data.get('activity_level_id'):
                        pet.activity_level = ActivityLevel.objects.get(pk=pet_data['activity_level_id'])
                    if pet_data.get('treat_frequency_id'):
                        pet.treat_frequency = TreatFrequency.objects.get(pk=pet_data['treat_frequency_id'])
                    
                    # Handle simple fields
                    pet.neutered = pet_data.get('neutered')
                    pet.age_years = pet_data.get('age_years')
                    pet.age_months = pet_data.get('age_months')
                    pet.age_weeks = pet_data.get('age_weeks')
                    pet.unknown_breed = pet_data.get('unknown_breed')
                    pet.food_allergy_other = pet_data.get('food_allergy_other')
                    
                    # Handle weight conversion
                    if pet_data.get('weight'):
                        from decimal import Decimal
                        pet.weight = Decimal(pet_data['weight'])
                    
                    pet.save()
                    
                    # Handle many-to-many relationships
                    if pet_data.get('food_types_ids'):
                        food_types = FoodType.objects.filter(pk__in=pet_data['food_types_ids'])
                        pet.food_types.set(food_types)
                    
                    if pet_data.get('food_allergies_ids'):
                        food_allergies = FoodAllergy.objects.filter(pk__in=pet_data['food_allergies_ids'])
                        pet.food_allergies.set(food_allergies)
                    
                    if pet_data.get('health_issues_ids'):
                        health_issues = HealthIssue.objects.filter(pk__in=pet_data['health_issues_ids'])
                        pet.health_issues.set(health_issues)
                    
                    pet_created = True
                    print(f"✅ Pet '{pet_name}' created during activation for user {user.email}")  # Debug log
                
                # Clear the session data
                del request.session[pending_pet_key]
                
            except Exception as e:
                print(f"❌ Error during pet creation at activation: {e}")  # Debug log
                # If pet creation fails, still proceed with activation
                if pending_pet_key in request.session:
                    del request.session[pending_pet_key]
        
        # Store activation info in session for password setup
        request.session['newly_activated_user_id'] = user.pk
        if pet_created and pet_name:
            request.session['activated_with_pet'] = pet_name
        
        # Redirect to password setup instead of login
        return redirect('set_password_after_activation')
    else:
        messages.error(request, _("Activation link is invalid!"))
        return redirect('login')


def set_password_after_activation(request):
    """Set password after email activation"""
    # Check if user just activated their account
    if 'newly_activated_user_id' not in request.session:
        messages.error(request, _("Invalid access. Please use the activation link from your email."))
        return redirect('login')
    
    user_id = request.session['newly_activated_user_id']
    pet_name = request.session.get('activated_with_pet')
    
    try:
        User = get_user_model()
        user = User.objects.get(pk=user_id, is_active=True)
    except User.DoesNotExist:
        messages.error(request, _("User not found or not activated."))
        return redirect('login')
    
    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            # Set the new password
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Clear session data
            del request.session['newly_activated_user_id']
            if 'activated_with_pet' in request.session:
                del request.session['activated_with_pet']
            
            # Log the user in automatically
            from django.contrib.auth import login
            login(request, user)
            
            # Show success message
            if pet_name:
                messages.success(request, _(f"🎉 Welcome to FAMO-PET! Your password has been set and {pet_name}'s profile is ready!"))
                return redirect('pet:my_pets')
            else:
                messages.success(request, _("🎉 Welcome to FAMO-PET! Your password has been set successfully!"))
                return redirect('dashboard')
        else:
            messages.error(request, _("Please correct the errors below."))
    else:
        form = SetPasswordForm()
    
    context = {
        'form': form,
        'user_email': user.email,
        'pet_name': pet_name,
    }
    return render(request, 'userapp/set_password.html', context)

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_dashboard_view(request):
    User = get_user_model()
    total_users = User.objects.count()
    total_pets = Pet.objects.count()
    total_dogs = Pet.objects.filter(pet_type__name__iexact="Dog").count()
    total_cats = Pet.objects.filter(pet_type__name__iexact="Cat").count()
    total_ai_meals = AIRecommendation.objects.count()
    total_ai_health = AIHealthReport.objects.count()

    # Gather all IPs from AIRecommendation and AIHealthReport
    ai_meal_ips = AIRecommendation.objects.values_list('ip_address', flat=True)
    ai_health_ips = AIHealthReport.objects.values_list('ip_address', flat=True)
    all_ips = list(ai_meal_ips) + list(ai_health_ips)

    # Get country for each IP (skip empty/null)
    countries = [get_country_from_ip(ip) for ip in all_ips if ip]
    country_counts = Counter(countries)
    top_countries = country_counts.most_common(10)

    context = {
        'total_users': total_users,
        'total_pets': total_pets,
        'total_dogs': total_dogs,
        'total_cats': total_cats,
        'total_ai_meals': total_ai_meals,
        'total_ai_health': total_ai_health,
        'top_countries': top_countries,
    }
    return render(request, 'userapp/admin_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def export_users_csv(request):
    User = get_user_model()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    # Write header
    writer.writerow(['ID', 'Email', 'Full Name', 'Date Joined', 'Is Staff', 'Is Superuser'])
    # Write data
    for user in User.objects.all():
        # Get full name from profile if exists
        if hasattr(user, 'profile'):
            full_name = f"{user.profile.first_name} {user.profile.last_name}".strip()
        else:
            full_name = ""
        writer.writerow([
            user.id,
            user.email,
            full_name,
            user.date_joined,
            user.is_staff,
            user.is_superuser
        ])
    return response
