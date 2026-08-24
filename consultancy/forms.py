from django import forms
from .models import *

class PatientRegisterForm(forms.Form):

    name = forms.CharField(
        max_length=100
    )

    email = forms.EmailField()

    password = forms.CharField(
        widget=forms.PasswordInput
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )
    
class PatientLoginForm(forms.Form):

    email = forms.EmailField()

    password = forms.CharField(
        widget=forms.PasswordInput
    )
    
    
class AvailabilityForm(forms.Form):

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date"
            }
        )
    )

    session = forms.ChoiceField(
        choices=(
            ("morning", "Morning"),
            ("afternoon", "Afternoon"),
            ("evening", "Evening"),
        )
    )
    
class DoctorRegisterForm(forms.Form):

    name = forms.CharField(
        max_length=100
    )

    email = forms.EmailField()

    password = forms.CharField(
        widget=forms.PasswordInput
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    category = forms.ModelChoiceField(
        queryset=DoctorCategory.objects.all()
    )

    qualification = forms.CharField(
        max_length=200
    )

    experience = forms.IntegerField(
        min_value=0
    )

    consultation_fee = forms.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    about = forms.CharField(
        widget=forms.Textarea,
        required=False
    )
    
class DoctorLoginForm(forms.Form):

    email = forms.EmailField()

    password = forms.CharField(
        widget=forms.PasswordInput
    )
    
class DoctorProfileForm(forms.Form):

    name = forms.CharField(
        max_length=100
    )

    qualification = forms.CharField(
        max_length=200
    )

    experience = forms.IntegerField(
        min_value=0
    )

    consultation_fee = forms.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    about = forms.CharField(
        widget=forms.Textarea,
        required=False
    )

    is_available = forms.BooleanField(
        required=False
    )


class PatientProfileForm(forms.ModelForm):

    class Meta:

        model = PatientProfile

        fields = [
            "date_of_birth",
            "gender",
            "height",
            "weight",
            "blood_group",
            "allergies",
            "existing_conditions",
            "current_medications",
        ]

        widgets = {

            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date"
                }
            ),

            "height": forms.NumberInput(
                attrs={
                    "placeholder": "Height in cm"
                }
            ),

            "weight": forms.NumberInput(
                attrs={
                    "placeholder": "Weight in kg"
                }
            ),

            "allergies": forms.Textarea(
                attrs={
                    "placeholder": "Example: Penicillin allergy",
                    "rows": 3
                }
            ),

            "existing_conditions": forms.Textarea(
                attrs={
                    "placeholder": "Example: Diabetes, asthma, etc.",
                    "rows": 3
                }
            ),

            "current_medications": forms.Textarea(
                attrs={
                    "placeholder": "Medicines currently taking",
                    "rows": 3
                }
            ),
        }