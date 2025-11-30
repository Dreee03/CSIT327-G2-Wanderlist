from django import forms
from .models import UserProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'first_name', 'last_name', 'middle_initial', 'age', 'bio', 'profile_pic']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_initial': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M.I.'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about yourself...'}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }

# ✅ ADD THIS NEW FORM CLASS
class ChangePasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'minlength': '6', 'placeholder': 'New password'}),
        help_text="Minimum 6 characters."
    )
    confirm_password = forms.CharField(
        label="Confirm Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data