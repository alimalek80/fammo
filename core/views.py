from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import HeroSection
from .forms import HeroSectionForm

def home(request):
    # Get the currently active hero section
    hero_section = HeroSection.objects.filter(is_active=True).first()
    return render(request, 'core/home.html', {'hero': hero_section})

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_hero_section(request):
    # Get the first hero section instance, or create one if it doesn't exist
    hero_section, created = HeroSection.objects.get_or_create(
        id=1, 
        defaults={
            'heading': 'Default Heading',
            'subheading': 'Default subheading text.',
            'button_text': 'Get Started',
            'button_url': '#'
        }
    )
    
    if request.method == 'POST':
        form = HeroSectionForm(request.POST, request.FILES, instance=hero_section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hero section updated successfully!')
            return redirect('manage_hero_section')
    else:
        form = HeroSectionForm(instance=hero_section)
        
    return render(request, 'core/manage_hero_section.html', {'form': form})