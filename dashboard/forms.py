from django import forms
from .models import UserProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        
        # ✅ ADDED new fields
        fields = ['email', 'first_name', 'last_name', 'middle_initial', 'age', 'bio', 'profile_pic']
        
        # ✅ ADDED widgets for new fields
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_initial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M.I.'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }