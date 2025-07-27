from django import forms
from .models import Pet, AgeCategory, Breed

BOOLEAN_CHOICES = [(True, 'Yes'), (False, 'No')]

class PetForm(forms.ModelForm):
    neutered = forms.ChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.RadioSelect(),
        required=True,
        label="Is your pet neutered?"
    )

    class Meta:
        model = Pet
        exclude = ['user']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md',
                'placeholder': 'e.g. Manti'
            }),
            'pet_type': forms.RadioSelect(),  # <-- Use RadioSelect, not Select
            'gender': forms.RadioSelect(),
            'neutered': forms.RadioSelect(),
            'age_category': forms.RadioSelect(),
            'age_years': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md',
                'placeholder': 'Years'
            }),
            'age_months': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md',
                'placeholder': 'Months'
            }),
            'age_weeks': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md',
                'placeholder': 'Weeks'
            }),
            'breed': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-md'}),
            'food_types': forms.CheckboxSelectMultiple(),
            'food_feeling': forms.RadioSelect(),
            'food_importance': forms.RadioSelect(),
            'body_type': forms.RadioSelect(),
            'weight': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded-md'}),
            'activity_level': forms.RadioSelect(),
            'food_allergies': forms.CheckboxSelectMultiple(),
            'food_allergy_other': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded-md'}),
            'health_issues': forms.CheckboxSelectMultiple(),
            'treat_frequency': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set breed queryset to empty initially for create form
        self.fields['breed'].queryset = Breed.objects.none()

        # If form is bound to data (POST request)
        if 'pet_type' in self.data:
            try:
                pet_type_id = int(self.data.get('pet_type'))
                self.fields['breed'].queryset = Breed.objects.filter(pet_type_id=pet_type_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input, queryset remains empty
        # If form is for an existing instance (edit form, GET request)
        elif self.instance.pk and self.instance.pet_type:
            self.fields['breed'].queryset = self.instance.pet_type.breeds.order_by('name')

        # Remove empty labels
        radio_fields = ['pet_type', 'gender', 'age_category', 'body_type', 'activity_level', 'food_feeling', 'food_importance', 'treat_frequency']
        for field_name in radio_fields:
            if field_name in self.fields:
                self.fields[field_name].empty_label = None

