from django import forms
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Profile
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Confirm Password"), widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email']

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 != p2:
            raise forms.ValidationError(_("Passwords do not match"))
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none transition-all duration-200 text-gray-900 bg-white'
            })

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email Address"),
        widget=forms.EmailInput(attrs={'autofocus': True})
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'phone', 'address', 'city', 'zip_code', 'country']
        labels = {
            'first_name': _("First Name"),
            'last_name': _("Last Name"),
            'phone': _("Phone"),
            'address': _("Address"),
            'city': _("City"),
            'zip_code': _("ZIP Code"),
            'country': _("Country"),
        }
        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 text-gray-900 bg-white'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_classes = 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-200 text-gray-900 bg-white'
        for name, field in self.fields.items():
            if name != 'address':  # address already styled above
                field.widget.attrs.update({'class': tailwind_classes})
