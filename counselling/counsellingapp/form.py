from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from counsellingapp.models import Appointment, CounselorAvailability, User

class RoleLoginForm(forms.Form):
    ROLE_CHOICES = [
        ('', 'Select Role'),
        ('admin', 'Admin'),
        ('counselor', 'Counselor'),
        ('student', 'Student'),
    ]

    email = forms.EmailField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Enter Email'}))
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

class LoginForm(forms.Form):
    email = forms.EmailField(max_length=200, widget=forms.TextInput(attrs={'placeholder': 'Enter Email'}))
    password = forms.CharField(max_length=200, widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}))
    role = forms.ChoiceField(choices=RoleLoginForm.ROLE_CHOICES, required=True)


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username'}
        )
    )
    phone = forms.CharField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Phone Number'}
        )
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'}
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}
        ),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone', 'is_admin', 'is_counselor', 'is_student']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date', 'time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
class CounselorForm(UserCreationForm):
    phone = forms.CharField(max_length=15, required=True, help_text="Phone number")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_counselor = True  # Set the user as a counselor
        if commit:
            user.save()
        return user
        
class CounselorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = CounselorAvailability
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

