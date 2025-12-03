from django import forms
from django.contrib.auth.models import User
from .models import Profile, Task

# --- User Authentication Forms ---
class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirm Password do not match."
            )

# --- Profile Management Forms ---
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "phone", "bio", "profile_image"]
# forms.py

from django import forms
from .models import Task # Make sure to import Task

# --- Task Management Forms ---
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'status', 'priority', 'due_date']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            
            # 💡 FIX: Changed to DateInput and type='date' to remove the time component
            'due_date': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d' # Format required for HTML5 date input (no time)
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes to all fields
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control'
            })