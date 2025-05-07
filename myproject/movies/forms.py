# movies/forms.py
from django import forms
from .models import Review, Movie, MemoryNote
from django.utils import timezone

class MemoryNoteForm(forms.ModelForm):
    class Meta:
        model = MemoryNote
        fields = ['note_title', 'note_body', 'unlock_on']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date().isoformat()
        self.fields['unlock_on'].widget = forms.DateInput(
            attrs={'type': 'date', 'min': today}
        )

    def clean_unlock_on(self):
        unlock_on = self.cleaned_data['unlock_on']
        if unlock_on < timezone.now().date():
            raise forms.ValidationError("Unlock date cannot be in the past.")
        return unlock_on

class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for movies...'
        })
    )

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['user', 'content', 'rating']
        widgets = {
            'user': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your review here...',
                'rows': 4
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[(i, f"{i} Stars") for i in range(1, 6)])
        }