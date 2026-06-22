from django import forms
from django.contrib.auth.forms import AuthenticationForm #validación de usuario y contraseña
from .models import Registro
from django import forms
from .models import Paquetes
from .models import Perfil

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['foto']

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
        fields = [
            "tipo_usuario",
            "nombre",
            "tipo_documento",
            "documento",
            "telefono",
            "email",
            "torre",
            "parqueadero",
            "placa",
            "observaciones"
        ]


from .models import Ingreso

class IngresoForm(forms.ModelForm):

    class Meta:
        model = Ingreso

        fields = [

            "tipo_ingreso",
            "nombre",
            "tipo_documento",
            "documento",
            "visita_a",
            "placa",
            "empresa",
            "estado",
            "observaciones"

        ]

        widgets = {

            "tipo_ingreso": forms.Select(attrs={"class": "input"}),
            "nombre": forms.TextInput(attrs={"class": "input"}),
            "tipo_documento": forms.Select(attrs={"class": "input"}),
            "documento": forms.TextInput(attrs={"class": "input"}),
            "visita_a": forms.TextInput(attrs={"class": "input"}),
            "placa": forms.TextInput(attrs={"class": "input"}),
            "empresa": forms.TextInput(attrs={"class": "input"}),
            "estado": forms.Select(attrs={"class": "input"}),
            "observaciones": forms.TextInput(attrs={"class": "input"}),

        }