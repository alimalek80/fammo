from django.shortcuts import render, redirect, get_object_or_404
from .forms import PetForm
from .models import Pet
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Breed


@login_required
def pet_form_view(request, pk=None):
    if pk:
        pet = get_object_or_404(Pet, pk=pk, user=request.user)
    else:
        pet = None

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

    context = {
        'form': form,
        'is_edit': bool(pet),
    }
    return render(request, 'pet/pet_form.html', context)

def load_breeds(request):
    pet_type_id = request.GET.get('pet_type')
    breeds = Breed.objects.filter(pet_type_id=pet_type_id).order_by('name')
    return JsonResponse(list(breeds.values('id', 'name')), safe=False)

@login_required
def my_pets_view(request):
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


