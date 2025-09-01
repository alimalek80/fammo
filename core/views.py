from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import HeroSection, SocialLinks
from .models import HeroSection, SocialLinks, FAQ
from .forms import HeroSectionForm, SocialLinksForm, FAQForm

def home(request):
    # Get the currently active hero section
    hero_section = HeroSection.objects.filter(is_active=True).first()
    faqs = FAQ.objects.filter(is_published=True).order_by("sort_order", "-updated_at")
    return render(request, 'core/home.html', {'hero': hero_section, "faqs": faqs})

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

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_social_links(request):
    links, created = SocialLinks.objects.get_or_create(id=1)
    if request.method == 'POST':
        form = SocialLinksForm(request.POST, instance=links)
        if form.is_valid():
            form.save()
            messages.success(request, "Social media links updated!")
            return redirect('manage_social_links')
    else:
        form = SocialLinksForm(instance=links)
    return render(request, 'core/manage_social_links.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_faqs(request):
    if request.method == "POST":
        form = FAQForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "FAQ added!")
            return redirect("manage_faqs")
    else:
        form = FAQForm()
    items = FAQ.objects.order_by("sort_order", "-updated_at")
    return render(request, "core/manage_faqs.html", {"form": form, "items": items})

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_faq(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    if request.method == "POST":
        form = FAQForm(request.POST, instance=faq)
        if form.is_valid():
            form.save()
            messages.success(request, "FAQ updated!")
            return redirect("manage_faqs")
    else:
        form = FAQForm(instance=faq)
    items = FAQ.objects.order_by("sort_order", "-updated_at")
    return render(request, "core/manage_faqs.html", {"form": form, "items": items, "edit_id": faq.id})

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_faq(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    faq.delete()
    messages.success(request, "FAQ deleted.")
    return redirect("manage_faqs")