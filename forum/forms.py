from django import forms
from .models import Question, Answer


class QuestionForm(forms.ModelForm):
    """Form for creating and editing questions"""
    
    class Meta:
        model = Question
        fields = ['title', 'category', 'body', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Why is my dog not eating?',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Provide as much detail as possible: pet age, breed, symptoms, duration, etc.'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }
        labels = {
            'title': 'Question Title',
            'category': 'Category',
            'body': 'Question Details',
            'image': 'Pet Photo (optional)',
        }


class AnswerForm(forms.ModelForm):
    """Form for creating and editing answers"""
    
    class Meta:
        model = Answer
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Share your knowledge and experience...'
            }),
        }
        labels = {
            'body': 'Your Answer',
        }
