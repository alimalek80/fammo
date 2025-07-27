from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegistrationForm, ProfileForm, CustomLoginForm
from .models import Profile
from django.contrib import messages
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model


def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _("Registration successful. Please complete your profile."))
            return redirect('update_profile')
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
    messages.info(request, _("Welcome to your dashboard!"))
    return render(request, 'userapp/dashboard.html')

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def users_admin_view(request):
    User = get_user_model()
    users = User.objects.all().prefetch_related('pets')
    
    return render(request, 'userapp/users_admin.html', {
        'users': users,
        
    })
