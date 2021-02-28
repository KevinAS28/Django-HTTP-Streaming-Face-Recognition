from django import forms
from .models import PatientProfile

class PatientCreation(forms.ModelForm):
  class Meta:
    model = PatientProfile
    exclude = ['user']
    widgets = {
      'date_of_birth': forms.TextInput(
        attrs={'type': 'date'}
      ),
    }

class SignUpForm(forms.Form):
  first_name = forms.CharField(max_length=100)
  last_name = forms.CharField(max_length=100)
  email = forms.EmailField()
