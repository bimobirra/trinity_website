from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *

car_condition_choices = [
    ('', '----------'),
    ('Very Bad', 'Very Bad'),
    ('Bad', 'Bad'),
    ('Average', 'Average'),
    ('Good', 'Good'),
    ('Very Good', 'Very Good'),
]

car_status_choices = [
    ('', '----------'),
    ('Available', 'Available'),
    ('Reserved', 'Reserved'),
    ('Sold', 'Sold'),
]

car_transmission_choices = [
    ('', '----------'),
    ('Automatic', 'Automatic'),
    ('Manual', 'Manual')
]

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
class CarForm(forms.ModelForm):
    
    condition = forms.ChoiceField(
        choices=car_condition_choices,
        required=True,
        label='Condition',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    transmission = forms.ChoiceField(
        choices=car_transmission_choices,
        required=True,
        label='Transmission',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Car
        fields = ['name', 'brand', 'transmission', 'color', 'interiorColor', 'model', 'trim', 'body', 'condition', 'odometer', 'image', 'price']
    
class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['color']
        
class InteriorColorForm(forms.ModelForm):
    class Meta:
        model = InteriorColor
        fields = ['color']
        
class BodyForm(forms.ModelForm):
    class Meta:
        model = Body
        fields = ['body']
        
class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'country_origin', 'founded_year']
