from django.db import models

# Create your models here.
class Cotizacion(models.Model):
    nombre = models.CharField(max_length=100)
    documento= models.CharField(max_length=20)
    telefono= models.CharField(max_length=11)
    email= models.EmailField(max_length=50)
    ciudad= models.CharField(max_length=50)
    consulta= models.TextField()
    
    
    
    def __str__(self):
        return self.nombre 
    
class Solicitud(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(max_length=20)
    tipo = models.CharField(max_length=50)
    mensaje = models.TextField()
    
    def __str__(self):
        return self.nombre 
    
class Registro(models.Model):
    tipo_usuario = models.CharField(max_length=50)
    nombre = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=50)
    documento = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=50, null=True, blank=True)
    torre = models.CharField(max_length=50)
    tarjeta = models.OneToOneField("Tarjeta", on_delete=models.PROTECT, unique=True, null=True, blank=True)
    parqueadero = models.CharField(max_length=10, null=True, blank=True, default= "...")
    placa = models.CharField(max_length=50, null=True, blank=True, default="...")
    fecha = models.DateField()
    hora_ingreso = models.TimeField()
    hora_salida = models.TimeField(null=True, blank=True)
    observaciones = models.CharField(max_length=50, null=True, blank=True, default="...")
    
    def __str__(self):
        return self.nombre 
    
class Usuario(models.Model):
    tipo_usuario = models.CharField(max_length=50)
    nombre = models.CharField(max_length=200)
    tipo_documento = models.CharField(max_length=50)
    documento = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(max_length=100)
    torre = models.CharField(max_length=50)
    parqueadero = models.CharField(max_length=10, null=True, blank=True)
    placa = models.CharField(max_length=50, null=True, blank=True)
    observaciones = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.nombre
  
class Paquetes(models.Model):
    destinatario = models.CharField(max_length=200)
    documento = models.CharField(max_length=50)
    nombre_recibe = models.CharField(max_length=200)
    torre = models.CharField(max_length=50)
    paquete = models.CharField(max_length=50)
    agencia = models.CharField(max_length=200)
    fecha = models.DateField()
    hora_ingreso = models.TimeField()
    hora_entrega = models.TimeField(null=True, blank=True)
    observaciones = models.CharField(max_length=50, null=True, blank=True, default="...")
  
    def __str__(self):
        return self.destinatario  

    
class Ip(models.Model):
    puerta = models.CharField(max_length=100)
    ip = models.CharField(max_length=50)
    estado = models.CharField(max_length=20)
    
    def __str__(self):
        return self.puerta
    
    
    
    
    
class AtencionCliente(models.Model):
    
    TIPO_SOLICITUD = [
        ('pregunta', 'Pregunta'),
        ('queja', 'Queja'),
        ('reclamo', 'Reclamo'),
        ('sugerencia', 'Sugerencia'),
        ('soporte', 'Soporte'),
    ]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    tipo = models.CharField(max_length=20, choices=TIPO_SOLICITUD)
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    


TIPO_ACCESO = [
    ("conjunto", "Acceso al conjunto"),
    ("torre", "Acceso a torre"),
]

TIPO_PUERTA = [
    ("principal", "Principal"),
    ("discapacitados", "Discapacitados"),
    ("vehiculos", "Vehículos"),
]

TORRES = [
    ("torre_1", "Torre 1"),
    ("torre_2", "Torre 2"),
    ("torre_3", "Torre 3"),
]

class RegistroAcceso(models.Model):
    persona = models.ForeignKey('Registro', on_delete=models.CASCADE)
    tipo_acceso = models.CharField(max_length=20, choices=TIPO_ACCESO)
    puerta = models.CharField(max_length=20, choices=TIPO_PUERTA, null=True, blank=True)
    torre = models.CharField(max_length=20, choices=TORRES, null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)
    hora_entrada = models.TimeField(auto_now_add=True)
    hora_salida = models.TimeField(null=True, blank=True)

    def __str__(self):
        if self.tipo_acceso == "conjunto":
            return f"{self.persona.nombre} - {self.puerta} - {self.fecha}"
        else:
            return f"{self.persona.nombre} - {self.torre} - {self.fecha}"
        
class Tarjeta(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    activa = models.BooleanField(default=True)
    def __str__(self):
        return self.numero
    
class Persona(models.Model):
    nombre = models.CharField(max_length=200)
    cedula = models.CharField(max_length=20, unique=True)
    torre = models.CharField(max_length=10)
    apartamento = models.CharField(max_length=10)
    tarjeta = models.OneToOneField(Tarjeta, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.nombre
    

class HistorialTarjeta(models.Model):
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE)
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.registro} - {self.tarjeta.numero}"