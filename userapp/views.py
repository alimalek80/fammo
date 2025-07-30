from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserRegistrationForm, ProfileForm, CustomLoginForm
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
    messages.info(request, _("Welcome to your dashboard!"))
    return render(request, 'userapp/dashboard.html')

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
        messages.success(request, _("Your account has been activated. You can now log in."))
        return redirect('login')
    else:
        messages.error(request, _("Activation link is invalid!"))
        return redirect('login')
