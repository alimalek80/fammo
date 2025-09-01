from django import forms
from .models import HeroSection, SocialLinks, FAQ

class HeroSectionForm(forms.ModelForm):
    class Meta:
        model = HeroSection
        fields = [
            'heading',
            'subheading',
            'subheading_secondary',  # <-- add this line
            'button_text',
            'button_url',
            'background_image',
            'is_active'
        ]
        widgets = {
            'heading': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'subheading': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md', 'rows': 4}),
            'subheading_secondary': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-red-300 rounded-md text-red-600'}),  # <-- add this line
            'button_text': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'button_url': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md'}),
            'background_image': forms.ClearableFileInput(attrs={'class': 'w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'}),
        }

class SocialLinksForm(forms.ModelForm):
    class Meta:
        model = SocialLinks
        fields = ['instagram', 'x', 'facebook', 'linkedin']
        widgets = {
            'instagram': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'x': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'facebook': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'linkedin': forms.URLInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        }

class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ["question", "answer", "sort_order", "is_published"]
        widgets = {
            "question": forms.TextInput(attrs={"class": "w-full px-4 py-2 border rounded"}),
            "answer": forms.Textarea(attrs={"class": "w-full px-4 py-2 border rounded h-28"}),
            "sort_order": forms.NumberInput(attrs={"class": "w-full px-4 py-2 border rounded"}),
            "is_published": forms.CheckboxInput(attrs={"class": "h-5 w-5"}),
        }