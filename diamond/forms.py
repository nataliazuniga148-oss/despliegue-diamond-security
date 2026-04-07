from django import forms
from django.contrib.auth.forms import AuthenticationForm #validación de usuario y contraseña
from .models import Registro
from django import forms
from .models import Paquetes

class PaquetesForm(forms.ModelForm):
    class Meta:
        model = Paquetes
        fields = '__all__'


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Ingrese su usuario'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'input',
            'placeholder': 'Ingrese su contraseña'
        })
    )
    
        
class RegistroForm(forms.ModelForm):
    class Meta:
        model = Registro
        exclude = ['fecha',"hora_ingreso", 'hora_salida']

