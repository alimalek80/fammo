from django.shortcuts import render, redirect, get_object_or_404
from .forms import PetForm
from .models import Pet
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models import Breed, PetType, AgeCategory
from django.contrib import messages
import csv
from django.http import HttpResponse


@login_required
def pet_form_view(request, pk=None):
    if pk:
        pet = get_object_or_404(Pet, pk=pk, user=request.user)
    else:
        pet = None

    # --- LIMITATION LOGIC: Only when adding a new pet ---
    if not pet:  # Only check limit when adding, not editing
        user = request.user
        if not user.is_staff:
            profile = getattr(user, 'profile', None)
            plan = getattr(profile, 'subscription_plan', None)
            if plan:
                pet_limit = plan.pet_limit() if hasattr(plan, 'pet_limit') else 1
                current_pet_count = Pet.objects.filter(user=user).count()
                if current_pet_count >= pet_limit:
                    messages.error(request, f"You can only add up to {pet_limit} pets with your current plan.")
                    return redirect('pet:my_pets')

    if request.method == 'POST':
        form = PetForm(request.POST, instance=pet)
        if form.is_valid():
            new_pet = form.save(commit=False)
            new_pet.user = request.user
            new_pet.save()
            form.save_m2m()
            return redirect('pet:my_pets')  # Replace with your pets list view name
    else:
        form = PetForm(instance=pet)

    # Get PetType objects for Cat and Dog
    cat_type = PetType.objects.filter(name__iexact='Cat').first()
    dog_type = PetType.objects.filter(name__iexact='Dog').first()
    cat_ages = AgeCategory.objects.filter(pet_type=cat_type) if cat_type else []
    dog_ages = AgeCategory.objects.filter(pet_type=dog_type) if dog_type else []

    context = {
        'form': form,
        'is_edit': bool(pet),
        'cat_ages': cat_ages,
        'dog_ages': dog_ages,
    }
    return render(request, 'pet/pet_form.html', context)

def load_breeds(request):
    pet_type_id = request.GET.get('pet_type')
    breeds = Breed.objects.filter(pet_type_id=pet_type_id).order_by('name')
    return JsonResponse(list(breeds.values('id', 'name')), safe=False)

def my_pets_view(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to view your pets.")
        return redirect('login')  # Use your login URL name
    pets = request.user.pets.all()
    return render(request, 'pet/my_pets.html', {'pets': pets})

@login_required
def delete_pet_view(request, pk):
    pet = get_object_or_404(Pet, pk=pk, user=request.user)
    
    if request.method == "POST":
        pet.delete()
        return redirect('pet:my_pets')
    
    # If somehow accessed via GET (not expected), redirect safely
    return redirect('pet:my_pets')

@login_required
def pet_detail_view(request, pk):
    pet = get_object_or_404(Pet, pk=pk, user=request.user)
    return render(request, 'pet/pet_detail.html', {'pet': pet})

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def export_pets_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="pets.csv"'

    writer = csv.writer(response)
    # Write header (all fields)
    writer.writerow([
        'ID', 'Name', 'User Email', 'Type', 'Gender', 'Neutered', 'Age Category',
        'Age (years)', 'Age (months)', 'Age (weeks)', 'Breed', 'Food Types',
        'Food Feeling', 'Food Importance', 'Body Type', 'Weight', 'Activity Level',
        'Food Allergies', 'Other Food Allergy', 'Health Issues', 'Treat Frequency'
    ])
    # Write data
    for pet in Pet.objects.select_related(
        'user', 'pet_type', 'gender', 'age_category', 'breed', 'food_feeling',
        'food_importance', 'body_type', 'activity_level', 'treat_frequency'
    ).prefetch_related('food_types', 'food_allergies', 'health_issues').all():
        writer.writerow([
            pet.id,
            pet.name,
            pet.user.email,
            pet.pet_type.name if pet.pet_type else '',
            pet.gender.name if pet.gender else '',
            'Yes' if pet.neutered else 'No',
            pet.age_category.name if pet.age_category else '',
            pet.age_years or '',
            pet.age_months or '',
            pet.age_weeks or '',
            pet.breed.name if pet.breed else '',
            ', '.join([ft.name for ft in pet.food_types.all()]),
            pet.food_feeling.name if pet.food_feeling else '',
            pet.food_importance.name if pet.food_importance else '',
            pet.body_type.name if pet.body_type else '',
            pet.weight or '',
            pet.activity_level.name if pet.activity_level else '',
            ', '.join([fa.name for fa in pet.food_allergies.all()]),
            pet.food_allergy_other or '',
            ', '.join([hi.name for hi in pet.health_issues.all()]),
            pet.treat_frequency.name if pet.treat_frequency else '',
        ])
    return response


