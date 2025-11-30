from django import forms
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Clinic, VetProfile, WorkingHours

User = get_user_model()


class WorkingHoursFormSetBase(BaseInlineFormSet):
    """Custom formset to handle working hours validation"""
    
    def clean(self):
        super().clean()
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                is_closed = form.cleaned_data.get('is_closed', False)
                open_time = form.cleaned_data.get('open_time')
                close_time = form.cleaned_data.get('close_time')
                
                # If not closed, require both times
                if not is_closed and (not open_time or not close_time):
                    form.add_error('open_time', 'Opening and closing times are required when not closed.')
                
                # If closed, clear the times
                if is_closed:
                    form.cleaned_data['open_time'] = None
                    form.cleaned_data['close_time'] = None


# Working Hours Formset
WorkingHoursFormSet = inlineformset_factory(
    Clinic,
    WorkingHours,
    formset=WorkingHoursFormSetBase,
    fields=['day_of_week', 'is_closed', 'open_time', 'close_time'],
    extra=0,  # No extra forms since we auto-create all 7 days
    max_num=7,
    min_num=7,  # Require all 7 days
    validate_min=True,
    can_delete=False,
    widgets={
        'day_of_week': forms.HiddenInput(),
        'is_closed': forms.CheckboxInput(attrs={'class': 'day-closed-checkbox'}),
        'open_time': forms.TimeInput(attrs={
            'type': 'time',
            'class': 'time-input',
        }),
        'close_time': forms.TimeInput(attrs={
            'type': 'time',
            'class': 'time-input',
        }),
    }
)


class ClinicRegistrationForm(forms.ModelForm):
    """Form for clinic registration"""
    
    # Owner information fields
    owner_email = forms.EmailField(
        label="Owner Email",
        help_text="This will be used to create your clinic management account"
    )
    owner_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password",
        min_length=8
    )
    owner_password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )
    
    # Veterinarian profile fields (optional)
    vet_name = forms.CharField(
        max_length=120,
        required=False,
        label="Lead Veterinarian Name",
        help_text="Optional: Name of the lead veterinarian"
    )
    degrees = forms.CharField(
        max_length=200,
        required=False,
        label="Degrees & Qualifications",
        help_text="e.g., DVM, MSc Nutrition"
    )
    certifications = forms.CharField(
        max_length=240,
        required=False,
        label="Certifications",
        widget=forms.Textarea(attrs={'rows': 3})
    )
    
    # Terms and conditions checkboxes
    agree_clinic_terms = forms.BooleanField(
        required=True,
        label="I have read and agree to FAMMO.ai's Terms and Conditions for Clinics",
        error_messages={'required': 'You must accept the Terms and Conditions to register.'}
    )
    
    agree_partnership = forms.BooleanField(
        required=True,
        label="I have read and agree to the FAMMO Clinic Partnership Agreement",
        error_messages={'required': 'You must accept the Partnership Agreement to register.'}
    )
    
    # Expression of Interest for pilot program
    clinic_eoi = forms.BooleanField(
        required=False,
        label="I confirm that our clinic is interested in participating in FAMMO's upcoming pilot program and receiving collaboration updates."
    )
    
    class Meta:
        model = Clinic
        fields = [
            'name', 'city', 'address', 'phone', 'email', 'website',
            'instagram', 'specializations', 'bio', 'logo', 'clinic_eoi'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'specializations': forms.TextInput(attrs={
                'placeholder': 'e.g., Dogs, Cats, Exotic Animals, Surgery'
            }),
            'instagram': forms.TextInput(attrs={
                'placeholder': '@yourclinicinsta or full URL'
            }),
            'address': forms.Textarea(attrs={'rows': 2}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("owner_password")
        password_confirm = cleaned_data.get("owner_password_confirm")
        owner_email = cleaned_data.get("owner_email")
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Passwords do not match.")
        
        # Check if user with this email already exists
        if owner_email and User.objects.filter(email=owner_email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        
        return cleaned_data


class ClinicProfileForm(forms.ModelForm):
    """Form for updating clinic profile"""
    
    class Meta:
        model = Clinic
        fields = [
            'name', 'city', 'address', 'latitude', 'longitude', 'phone', 'email', 'website',
            'instagram', 'specializations', 'working_hours', 'bio', 'logo'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'specializations': forms.TextInput(attrs={
                'placeholder': 'e.g., Dogs, Cats, Exotic Animals, Surgery'
            }),
            'working_hours': forms.TextInput(attrs={
                'placeholder': 'e.g., Mon-Fri 9:00-18:00, Sat 9:00-14:00'
            }),
            'instagram': forms.TextInput(attrs={
                'placeholder': '@yourclinicinsta or full URL'
            }),
            'address': forms.Textarea(attrs={'rows': 2}),
            'latitude': forms.NumberInput(attrs={
                'placeholder': 'e.g., 52.3676',
                'step': '0.000001'
            }),
            'longitude': forms.NumberInput(attrs={
                'placeholder': 'e.g., 4.9041',
                'step': '0.000001'
            }),
        }
        help_texts = {
            'latitude': 'Latitude coordinate (will be auto-detected from address if left empty)',
            'longitude': 'Longitude coordinate (will be auto-detected from address if left empty)',
        }


class VetProfileForm(forms.ModelForm):
    """Form for updating veterinarian profile"""
    
    class Meta:
        model = VetProfile
        fields = ['vet_name', 'degrees', 'certifications']
        widgets = {
            'certifications': forms.Textarea(attrs={'rows': 3}),
        }


class ReferralCodeForm(forms.Form):
    """Form for generating new referral codes"""
    
    code = forms.SlugField(
        max_length=40,
        help_text="Custom referral code (optional). If empty, a code will be generated automatically.",
        required=False
    )
    
    def __init__(self, clinic=None, *args, **kwargs):
        self.clinic = clinic
        super().__init__(*args, **kwargs)
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            # Check if code already exists
            from .models import ReferralCode
            if ReferralCode.objects.filter(code=code).exists():
                raise forms.ValidationError("This referral code is already taken.")
        return code


class ClinicSearchForm(forms.Form):
    """Form for searching clinics"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search clinics by name, city, or specialization...',
            'class': 'form-control'
        })
    )
    
    city = forms.CharField(
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'City',
            'class': 'form-control'
        })
    )
    
    verified_only = forms.BooleanField(
        required=False,
        label="Verified clinics only"
    )