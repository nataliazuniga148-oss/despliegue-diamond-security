from rest_framework import serializers
from .models import AtencionCliente
from .models import RegistroAcceso


class AtencionClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtencionCliente
        fields = '__all__'
        
class RegistroAccesoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RegistroAcceso
        fields = "__all__"
        