from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import timedelta
from django.utils import timezone
from PIL import Image


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)

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

    tarjeta = models.OneToOneField(
        "Tarjeta",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    parqueadero = models.CharField(max_length=10, null=True, blank=True, default="...")
    placa = models.CharField(max_length=50, null=True, blank=True, default="...")
    fecha = models.DateField()
    hora_registro = models.TimeField()
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
    
    ESTADOS = [
        ("Pendiente", "Pendiente"),
        ("Entregado", "Entregado"),
    ]

    destinatario = models.CharField(
        max_length=200
    )

    documento = models.CharField(
        max_length=50
    )

    nombre_recibe = models.CharField(
        max_length=200
    )

    torre = models.CharField(
        max_length=50
    )

    paquete = models.CharField(
        max_length=50
    )

    agencia = models.CharField(
        max_length=200
    )

    fecha = models.DateField()

    hora_ingreso = models.TimeField()

    hora_entrega = models.TimeField(
        null=True,
        blank=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Pendiente"
    )

    entregado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paquetes_entregados"
    )

    observaciones = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        default="..."
    )

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
    persona = models.ForeignKey('Registro',on_delete=models.CASCADE,null=True,blank=True)
    tipo_acceso = models.CharField(max_length=20, choices=TIPO_ACCESO)
    puerta = models.CharField(max_length=20, choices=TIPO_PUERTA, null=True, blank=True)
    torre = models.CharField(max_length=20, choices=TORRES, null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)
    hora_entrada = models.TimeField(auto_now_add=True)
    hora_salida = models.TimeField(null=True, blank=True)
    estado = models.CharField(max_length=400, default="permitido")
    motivo = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        if self.tipo_acceso == "conjunto":
            return f"{self.persona.nombre} - {self.puerta} - {self.fecha}"
        else:
            return f"{self.persona.nombre} - {self.torre} - {self.fecha}"


class Puerta(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_PUERTA)
    torre = models.CharField(max_length=20, choices=TORRES, null=True, blank=True)
    estado = models.BooleanField(default=False)  
    emergencia = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre



class Tarjeta(models.Model):
    
    numero = models.CharField(
        max_length=20,
        unique=True
    )

    activa = models.BooleanField(
        default=True
    )

    puertas = models.ManyToManyField(
        Puerta,
        blank=True
    )

    # NUEVO
    intentos_fallidos = models.IntegerField(
        default=0
    )

    # NUEVO
    bloqueada = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.numero

class HistorialTarjeta(models.Model):
    ACCIONES = [
        ("asignada", "Asignada"),
        ("activada", "Activada"),
        ("desactivada", "Desactivada"),
        ("cambiada", "Cambiada"),
        ("editada", "Editada"),
    ]

    registro = models.ForeignKey(Registro, on_delete=models.CASCADE, null=True, blank=True)
    tarjeta = models.ForeignKey(Tarjeta, on_delete=models.CASCADE)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    fecha = models.DateTimeField(auto_now_add=True)

    def estado_legible(self):
        if self.accion == "activada":
            return "Tarjeta activa"
        elif self.accion == "desactivada":
            return "Tarjeta desactivada"
        elif self.accion == "cambiada":
            return "Tarjeta cambiada"
        elif self.accion == "asignada":
            return "Tarjeta asignada"
        elif self.accion == "editada":
            return "Tarjeta editada"
        return self.accion


class Dispositivo(models.Model):
    puerta = models.OneToOneField(Puerta, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    estado = models.CharField(max_length=20, default="inactivo")

    def __str__(self):
        return f"{self.puerta.nombre} - {self.ip}"
    


class Ingreso(models.Model):

    TIPO_INGRESO = [
        ('visitante_temporal', 'Visitante temporal'),
        ('proveedor', 'Proveedor'),
        ('domiciliario', 'Domiciliario'),
    ]

    TIPO_DOCUMENTO = [
        ('cc', 'Cédula de ciudadanía'),
        ('ce', 'Cédula de extranjería'),
        ('pasaporte', 'Pasaporte'),
        ('ti', 'Tarjeta de identidad'),
    ]

    tipo_ingreso = models.CharField(
        max_length=30,
        choices=TIPO_INGRESO
    )

    nombre = models.CharField(
        max_length=100
    )

    tipo_documento = models.CharField(
        max_length=20,
        choices=TIPO_DOCUMENTO
    )

    documento = models.CharField(
        max_length=30
    )

    visita_a = models.CharField(
        max_length=100
    )

    placa = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    empresa = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    fecha = models.DateField()
    hora_ingreso = models.TimeField()

    hora_salida = models.TimeField(
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        default='Dentro'
    )

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.nombre
    
    
class Perfil(models.Model):
    
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )

    foto = models.ImageField(
        upload_to='perfiles/',
        blank=True,
        null=True
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.foto:
            img = Image.open(self.foto.path)

            # 🔥 mejora calidad
            img = img.convert("RGB")

            # tamaño ideal
            img.thumbnail((300, 300))

            # guardar con buena calidad
            img.save(self.foto.path, quality=95)

    def __str__(self):
        return self.usuario.username
from django.db import models


class ConfiguracionSistema(models.Model):

    bloqueo_automatico = models.BooleanField(default=True)

    cierre_automatico = models.CharField(
        max_length=20,
        default='10 minutos'
    )

    verificacion_adicional = models.BooleanField(default=False)

    alertas_correo = models.BooleanField(default=True)

    alertas_sonoras = models.BooleanField(default=False)

    actividad_sospechosa = models.BooleanField(default=True)

    guardar_historial = models.BooleanField(default=True)

    actividad_nocturna = models.BooleanField(default=True)

    tiempo_almacenamiento = models.CharField(
    max_length=20,
    default='6 meses'
    )

    rol_principal = models.CharField(
        max_length=30,
        default='Administrador'
    )

    edicion_usuarios = models.BooleanField(default=True)

    creacion_cuentas = models.BooleanField(default=False)

    modo_oscuro = models.BooleanField(default=False)

    version = models.CharField(
        max_length=20,
        default='v1.0.3'
    )

    def __str__(self):
        return "Configuración del sistema"
    
class Alerta(models.Model):
    TIPO = [
        ("INFO", "INFO"),
        ("WARNING", "WARNING"),
        ("ERROR", "ERROR"),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO)
    mensaje = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.mensaje}"
    


class TarjetaDesconocida(models.Model):
    
    uid = models.CharField(max_length=100, unique=True)

    intentos_fallidos = models.IntegerField(default=0)

    bloqueada = models.BooleanField(default=False)

    ultima_fecha = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.uid