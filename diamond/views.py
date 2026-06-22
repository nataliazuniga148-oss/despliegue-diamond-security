from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q, Max
from django.contrib.auth import logout
import difflib
import re
from django.http import JsonResponse
from .models import ConfiguracionSistema, Alerta
from datetime import date
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from django.db.models import Q
from xhtml2pdf import pisa
from django.core.mail import EmailMessage
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import EmailMessage
from .models import Ingreso

from .models import (Solicitud,
    Registro,
    Cotizacion,
    AtencionCliente,
    Puerta,
    RegistroAcceso,
    Tarjeta,
    HistorialTarjeta,
    Paquetes,
    Dispositivo
)
from rest_framework import viewsets
from .models import AtencionCliente
from .serializers import AtencionClienteSerializer


class AtencionClienteViewSet(viewsets.ModelViewSet):
    queryset = AtencionCliente.objects.all()
    serializer_class = AtencionClienteSerializer

from .forms import RegistroForm, PaquetesForm
from .serializers import AtencionClienteSerializer, RegistroAccesoSerializer
from django.conf import settings
import os
from django.conf import settings
from django.contrib.staticfiles import finders
import os
from django.conf import settings
from django.contrib.staticfiles import finders
import os
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from .models import PasswordResetToken
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import PasswordResetToken

from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from .models import PasswordResetToken
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from .models import PasswordResetToken
from django.core.mail import send_mail
from django.http import HttpResponse
from .forms import PerfilForm

from django.contrib.auth.decorators import login_required
from .models import Perfil
from .forms import RegistroForm, PaquetesForm, IngresoForm
from .models import ConfiguracionSistema
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import RegistroAcceso, Alerta
from django.contrib.auth.models import User, Group

from django.contrib.auth.models import User
def editar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)

    if request.method == "POST":
        usuario.username = request.POST.get("username")
        usuario.email = request.POST.get("email")

        # Rol (grupo)
        grupo_id = request.POST.get("grupo")

        if grupo_id:
            usuario.groups.clear()
            grupo = Group.objects.get(id=grupo_id)
            usuario.groups.add(grupo)

        usuario.save()
        return redirect("ver_usuarios")

    grupos = Group.objects.all()

    return render(request, "editar_usuario/editar_usuario.html", {
        "usuario": usuario,
        "grupos": grupos
    })
    
def cambiar_estado(request, id):
    # Obtener usuario o error 404 si no existe
    usuario = get_object_or_404(User, id=id)

    # Cambiar estado
    usuario.is_active = not usuario.is_active
    usuario.save()

    # Mensaje
    if usuario.is_active:
        messages.success(request, f"Usuario {usuario.username} activado correctamente.")
    else:
        messages.warning(request, f"Usuario {usuario.username} desactivado correctamente.")

    return redirect('ver_usuarios')

def ver_usuarios(request):
    
    # Traer usuarios ordenados
    usuarios_list = User.objects.all().order_by("id")

    # Paginación
    paginator = Paginator(usuarios_list, 5)
    page_number = request.GET.get("page")
    usuarios = paginator.get_page(page_number)

    # Renderizar
    return render(
        request,
        "ver_usuarios/ver_usuarios.html",
        {
            "usuarios": usuarios
        }
    )

def crear_usuario(request):
    
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]
        confirmar = request.POST["confirmar_password"]
        grupo = request.POST["grupo"]

        if password != confirmar:
            messages.error(request, "Las contraseñas no coinciden.")
            return redirect("crear_usuario")

        if User.objects.filter(username=username).exists():
            messages.error(request, "El usuario ya existe.")
            return redirect("crear_usuario")

        usuario = User.objects.create_user(
            username=username,
            password=password
        )

        grupo_obj = Group.objects.get(name=grupo)
        usuario.groups.add(grupo_obj)

        messages.success(request, "Usuario creado correctamente.")

        return redirect("crear_usuario")

    return render(request, "crear_usuario/crear_usuario.html")


@login_required
def monitoreo(request):
    
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(
            request,
            "No tienes permisos para acceder al centro de monitoreo"
        )
        return redirect("cliente")

    alertas_list = Alerta.objects.all().order_by("-id")

    paginator = Paginator(alertas_list, 10)  # 10 alertas por página

    page_number = request.GET.get("page")
    alertas = paginator.get_page(page_number)

    return render(
        request,
        "monitoreo/monitoreo.html",
        {
            "alertas": alertas
        }
    )
    
@login_required
def alertas_api(request):

    alertas = list(
        Alerta.objects.order_by("-id").values(
            "tipo", "mensaje", "fecha"
        )[:8]
    )

    return JsonResponse({"alertas": alertas})

def get_config():
    return ConfiguracionSistema.objects.get(id=1)





@login_required
def cambiar_foto(request):

    # Obtener o crear perfil
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=perfil)

        if form.is_valid():
            if 'foto' in request.FILES:
                perfil.foto = request.FILES['foto']  # asigna la nueva imagen

            form.save()

            
            print("Foto guardada:", perfil.foto)

            return redirect('cliente')

        else:
            print("Errores del formulario:", form.errors)

    else:
        form = PerfilForm(instance=perfil)

    return render(request, 'cambiar_foto/cambiar_foto.html', {
        'form': form,
        'perfil': perfil
    })

def restablecer(request, token):
    token_obj = PasswordResetToken.objects.filter(
        token=token,
        used=False
    ).first()

    if not token_obj:
        return render(request, "diamond/error.html", {
            "mensaje": "Token inválido"
        })

    if timezone.now() > token_obj.created_at + timedelta(minutes=15):
        return render(request, "diamond/error.html", {
            "mensaje": "El enlace ha expirado (15 minutos)"
        })

    if request.method == "POST":
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            return render(request, "restablecer/restablecer.html", {
                "error": "Las contraseñas no coinciden",
                "token": token_obj
            })

        try:
            validate_password(password1, user=token_obj.user)
        except ValidationError as e:
            return render(request, "restablecer/restablecer.html", {
                "error": e.messages[0],
                "token": token_obj
            })

        user = token_obj.user
        user.password = make_password(password1)
        user.save()

        token_obj.used = True
        token_obj.save()

        messages.success(request, "Contraseña actualizada correctamente")

        return redirect("acceso")

    return render(request, "restablecer/restablecer.html", {
        "token": token_obj
    })

def recuperar(request):
    mensaje = ""

    if request.method == "POST":
        correo = request.POST.get("email")

        # Mensaje genérico (seguridad)
        mensaje = "Si el correo existe, recibirás un enlace para recuperar tu contraseña"

        # limpiar tokens expirados (recomendado)
        PasswordResetToken.objects.filter(
            created_at__lt=timezone.now() - timedelta(minutes=15),
            used=False
        ).delete()

        try:
            user = User.objects.get(email=correo)

            token_obj = PasswordResetToken.objects.create(user=user)


            link = request.build_absolute_uri(
                f"/restablecer/{token_obj.token}/"
            )

            send_mail(
                "Recuperación de contraseña",
                f"Ingresa al siguiente enlace para cambiar tu contraseña:\n{link}",
                settings.EMAIL_HOST_USER,
                [correo],
                fail_silently=False,
            )

        except User.DoesNotExist:
            pass  # no revelar existencia del usuario

    return render(request, "recuperar/recuperar.html", {
        "mensaje": mensaje
    })

def obtener_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]

    return request.META.get('REMOTE_ADDR')


@api_view(["POST"])
def registrar_acceso(request):


    # CONFIGURACIÓN (AÑADIDO)
  
    config = ConfiguracionSistema.objects.first()
    # CÓDIGO AÑADIDO DE CONFIGURACIÓN

    tarjeta = request.data.get("tarjeta")
    tipo_acceso = request.data.get("tipo_acceso")
    torre = request.data.get("torre")

    
    # NORMALIZAR TORRE ENVIADA
  
    if torre:

        torre_texto = str(torre).lower()

        match = re.search(r"(\d+)", torre_texto)

        if match:

            numero_torre = match.group(1)

            torre = f"torre_{numero_torre}"

  
    # VALIDAR TARJETA

    if not tarjeta:

        RegistroAcceso.objects.create(
            persona=None,
            tipo_acceso="conjunto",
            torre=torre if torre else None,
            puerta="principal",
            estado="denegado"
        )

        # ALERTA (AÑADIDO)
        if config and config.actividad_sospechosa:
            Alerta.objects.create(
                tipo="WARNING",
                mensaje="Intento de acceso sin tarjeta",
                usuario=None
            )
        # CÓDIGO AÑADIDO DE CONFIGURACIÓN

        return Response(
            {"error": "Debe enviar la tarjeta"},
            status=400
        )

    
    # VALIDAR TIPO ACCESO
  
    if not tipo_acceso:

        RegistroAcceso.objects.create(
            persona=None,
            tipo_acceso="conjunto",
            torre=torre if torre else None,
            puerta="principal",
            estado="denegado"
        )

        # ALERTA (AÑADIDO)
        if config and config.actividad_sospechosa:
            Alerta.objects.create(
                tipo="WARNING",
                mensaje="Intento de acceso sin tipo de acceso",
                usuario=None
            )
        # CÓDIGO AÑADIDO DE CONFIGURACIÓN

        return Response(
            {"error": "Debe enviar el tipo de acceso"},
            status=400
        )

    try:

        persona = Registro.objects.select_related(
            "tarjeta"
        ).get(
            tarjeta__numero=tarjeta,
            tarjeta__activa=True
        )

        tarjeta_obj = persona.tarjeta

        # =========================
        # OBTENER IP
        # =========================
        ip_cliente = obtener_ip(request)

        if not ip_cliente:

            RegistroAcceso.objects.create(
                persona=persona,
                tipo_acceso=tipo_acceso,
                torre=torre if torre else None,
                puerta="principal",
                estado="denegado"
            )

            return Response(
                {"error": "No se pudo obtener la IP"},
                status=400
            )

        posibles_ips = [ip_cliente]

        if ip_cliente == "127.0.0.1":
            posibles_ips.append("::1")

        elif ip_cliente == "::1":
            posibles_ips.append("127.0.0.1")

        try:

            dispositivo = Dispositivo.objects.select_related(
                "puerta"
            ).get(
                ip__in=posibles_ips,
                estado="activo"
            )

            puerta_obj = dispositivo.puerta

        except Dispositivo.DoesNotExist:

            RegistroAcceso.objects.create(
                persona=persona,
                tipo_acceso=tipo_acceso,
                torre=torre if torre else None,
                puerta="principal",
                estado="denegado"
            )

            # ALERTA (AÑADIDO)
            if config and config.actividad_sospechosa:
                Alerta.objects.create(
                    tipo="WARNING",
                    mensaje="Dispositivo no autorizado o inactivo",
                    usuario=None
                )
            # CÓDIGO AÑADIDO DE CONFIGURACIÓN

            return Response(
                {"error": "Dispositivo no autorizado o inactivo"},
                status=403
            )

        except Dispositivo.MultipleObjectsReturned:

            RegistroAcceso.objects.create(
                persona=persona,
                tipo_acceso=tipo_acceso,
                torre=torre if torre else None,
                puerta="principal",
                estado="denegado"
            )

            # ALERTA (AÑADIDO)
            if config and config.actividad_sospechosa:
                Alerta.objects.create(
                    tipo="ERROR",
                    mensaje="Configuración duplicada de dispositivos",
                    usuario=None
                )
            # CÓDIGO AÑADIDO DE CONFIGURACIÓN

            return Response(
                {"error": "Configuración duplicada de dispositivos"},
                status=500
            )

       
        # VALIDAR PUERTA
       
        if not puerta_obj:

            RegistroAcceso.objects.create(
                persona=persona,
                tipo_acceso=tipo_acceso,
                torre=torre if torre else None,
                puerta="principal",
                estado="denegado"
            )

            # ALERTA (AÑADIDO)
            if config and config.actividad_sospechosa:
                Alerta.objects.create(
                    tipo="WARNING",
                    mensaje="Puerta no configurada",
                    usuario=None
                )
            # CÓDIGO AÑADIDO DE CONFIGURACIÓN

            return Response(
                {"error": "Puerta no configurada"},
                status=500
            )

       
        # MODO EMERGENCIA
      
        if puerta_obj.emergencia:

            acceso = RegistroAcceso.objects.create(
                persona=persona,
                tipo_acceso="conjunto",
                puerta=puerta_obj.tipo,
                estado="permitido"
            )

            serializer = RegistroAccesoSerializer(acceso)

            return Response(serializer.data, status=201)



        if tipo_acceso == "conjunto":

            if not tarjeta_obj.puertas.filter(
                id=puerta_obj.id
            ).exists():

                RegistroAcceso.objects.create(
                    persona=persona,
                    tipo_acceso=tipo_acceso,
                    puerta=puerta_obj.tipo,
                    estado="denegado"
                )

                # ALERTA (AÑADIDO)
                if config and config.actividad_sospechosa:
                    Alerta.objects.create(
                        tipo="WARNING",
                        mensaje="Acceso denegado a puerta",
                        usuario=None
                    )
                # CÓDIGO AÑADIDO DE CONFIGURACIÓN

                return Response(
                    {"error": "Acceso denegado a esta puerta"},
                    status=403
                )

            puerta_registro = puerta_obj.tipo
            torre_registro = None

        # ACCESO TORRE

        elif tipo_acceso == "torre":

            if not torre:

                RegistroAcceso.objects.create(
                    persona=persona,
                    tipo_acceso=tipo_acceso,
                    estado="denegado"
                )

                return Response(
                    {"error": "Debe enviar la torre"},
                    status=400
                )

            torre_texto = str(persona.torre).lower()

            match = re.search(r"(\d+)", torre_texto)

            numero_bd = match.group(1) if match else None

            torre_bd = f"torre_{numero_bd}" if numero_bd else None

            if torre_bd != torre:

                RegistroAcceso.objects.create(
                    persona=persona,
                    tipo_acceso=tipo_acceso,
                    torre=torre,
                    estado="denegado"
                )

                return Response(
                    {"error": "Acceso denegado a torre"},
                    status=403
                )

            puerta_registro = None
            torre_registro = torre


        # PARQUEADERO

        elif tipo_acceso == "parqueadero":

            if not persona.parqueadero:

                RegistroAcceso.objects.create(
                    persona=persona,
                    tipo_acceso=tipo_acceso,
                    puerta="parqueadero",
                    estado="denegado"
                )

                return Response(
                    {"error": "Usuario sin parqueadero asignado"},
                    status=403
                )

            parqueadero_bd = "".join(filter(str.isdigit, str(persona.parqueadero)))

            puerta_registro = f"Parqueadero {parqueadero_bd}"
            torre_registro = None

        else:

            RegistroAcceso.objects.create(
                persona=None,
                tipo_acceso="conjunto",
                torre=torre if torre else None,
                puerta="principal",
                estado="denegado"
            )

            return Response(
                {"error": "Tipo de acceso inválido"},
                status=400
            )

        # =========================
        # SALIDA
        # =========================
        acceso_abierto = RegistroAcceso.objects.filter(
            persona=persona,
            estado="permitido",
            hora_salida__isnull=True
        ).last()

        if acceso_abierto:

            acceso_abierto.hora_salida = datetime.now().time()
            acceso_abierto.save()

            return Response(
                {"mensaje": "Salida registrada"},
                status=200
            )
            #actividad nocturna
        hora_actual = timezone.localtime().hour

        if (
                config
                and config.actividad_nocturna
                and (hora_actual >= 22 or hora_actual < 6)
               ):

                Alerta.objects.create(
                    tipo="WARNING",
                    mensaje=f"Acceso nocturno detectado: {persona.nombre}",
                    usuario=None
                )

        acceso = RegistroAcceso.objects.create(
            persona=persona,
            tipo_acceso=tipo_acceso,
            puerta=puerta_registro,
            torre=torre_registro,
            estado="permitido"
        )

        serializer = RegistroAccesoSerializer(acceso)

        return Response(serializer.data, status=201)

    except Registro.DoesNotExist:

       RegistroAcceso.objects.create(
           persona=None,
           tipo_acceso="conjunto",
           torre=torre if torre else None,
           puerta="principal",
           estado="denegado"
       )

       tarjeta_existe = Tarjeta.objects.filter(
           numero=tarjeta
       ).first()

       if tarjeta_existe:
           mensaje_alerta = "Tarjeta inactiva"
       else:
           mensaje_alerta = "Tarjeta no registrada"

       if config and config.actividad_sospechosa:
           Alerta.objects.create(
               tipo="ERROR",
               mensaje=mensaje_alerta,
               usuario=None
           )

       return Response(
           {"error": mensaje_alerta},
           status=404
       )
        # CÓDIGO AÑADIDO DE CONFIGURACIÓN



class AtencionClienteViewSet(viewsets.ModelViewSet):

    queryset = AtencionCliente.objects.all()

    serializer_class = AtencionClienteSerializer


def apertura_emergencia(request):
    if not request.user.groups.filter(
        name="Administrador"
    ).exists():

        messages.error(
            request,
            "No tienes permisos"
        )

        return redirect("cliente")

    if request.method == "POST":

        Puerta.objects.all().update(
            estado=True,
            emergencia=True
        )

        messages.warning(
            request,
            " MODO EMERGENCIA ACTIVADO"
        )

    return redirect("puertas")
def detener_emergencia(request):
    if request.method == "POST":
        Puerta.objects.all().update(
            emergencia=False
        )
        messages.success(request, "Modo emergencia desactivado")
    return redirect("puertas")


def cerrar_puertas(request):
    if request.method == "POST":
        Puerta.objects.all().update(
            estado=False,
            emergencia=False
        )
        messages.info(request, "Puertas cerradas correctamente")
    return redirect("puertas")

def cambiar_estado_puerta(request, id):
    puerta = get_object_or_404(Puerta, id=id)

    if request.method == "POST":
        puerta.estado = not puerta.estado
        puerta.save()

    return redirect("puertas")


def principal(request):
    return render(request, 'dashboard/principal.html')
def cerrar_sesion(request):
    logout(request)
    return redirect('principal')

def acceso(request):
    if request.method == 'POST':
        username = request.POST.get('usuario')
        password = request.POST.get('contrasena')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('cliente')
        else:
            return render(request, 'acceso/acceso.html', {'error': 'Usuario o contraseña incorrectos'})
    return render(request, 'acceso/acceso.html')



def registro(request):
    return render(request, 'registro/registro.html')

def cotizar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        documento = request.POST.get("documento")
        email = request.POST.get("email")
        telefono = request.POST.get("telefono")
        ciudad = request.POST.get("ciudad")
        consulta = request.POST.get("consulta")

        Cotizacion.objects.create(
            nombre=nombre,
            documento=documento,
            email=email,
            telefono=telefono,
            ciudad=ciudad,
            consulta=consulta
        )

        mensaje = f"""
Nueva solicitud de cotización.

Nombre: {nombre}
Documento: {documento}
Correo: {email}
Teléfono: {telefono}
Ciudad: {ciudad}

Consulta:
{consulta}
"""

        send_mail(
            "Nueva solicitud de cotización",
            mensaje,
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        messages.success(request, "Los datos han sido enviados correctamente.")
        return redirect("cotizar")

    return render(request, "cotizar/cotizar.html")

def contacto(request):
    return render(request, 'contacto/contacto.html')

def nosotros(request):
    return render(request, 'nosotros/nosotros.html')

def integraciones(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")
        tipo = request.POST.get("tipo")
        mensaje_usuario = request.POST.get("mensaje")

        Solicitud.objects.create(
            nombre=nombre,
            correo=correo,
            tipo=tipo,
            mensaje=mensaje_usuario
        )

        mensaje = f"""
Nuevo mensaje de atención al cliente.

Nombre: {nombre}
Correo: {correo}
Tipo de solicitud: {tipo}

Mensaje:
{mensaje_usuario}
"""

        send_mail(
            "Nuevo mensaje de atención al cliente",
            mensaje,
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        messages.success(request, "Los datos han sido enviados correctamente.")
        return redirect("integraciones")

    return render(request, "integraciones/integraciones.html")



def admin(request):
    return render(request, 'admin/admin.html')

def horarioad(request):
    return render(request, 'horarioad/horarioad.html')

def informes(request):
    return render(request, 'informes/informes.html')


def registroa(request):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")
    if request.method == "POST":

        tipo_usuario = request.POST.get("tipo_usuario")
        nombre = request.POST.get("nombre")
        tipo_documento = request.POST.get("tipo_documento")
        documento = request.POST.get("documento")
        telefono = request.POST.get("telefono")
        email = request.POST.get("email")
        torre = request.POST.get("torre")
        numero_tarjeta = request.POST.get("tarjeta")
        parqueadero = request.POST.get("parqueadero") or None
        placa = request.POST.get("placa") or None
        fecha = request.POST.get("fecha")
        hora_registro = request.POST.get("hora_ingreso")
        observaciones = request.POST.get("observaciones") or None

        if Registro.objects.filter(documento=documento).exists():
            return render(request, 'registroa/registroa.html', {
                'error': 'Este documento ya está registrado'
            })

        try:
            tarjeta_obj = None

            if numero_tarjeta:
                tarjeta_obj, created = Tarjeta.objects.get_or_create(
                    numero=numero_tarjeta,
                    defaults={"activa": True}
                )

                if Registro.objects.filter(tarjeta=tarjeta_obj).exists():
                    return render(request, 'registroa/registroa.html', {
                        'error': 'Esa tarjeta ya está asignada a otra persona'
                    })

            Registro.objects.create(
                tipo_usuario=tipo_usuario,
                nombre=nombre,
                tipo_documento=tipo_documento,
                documento=documento,
                telefono=telefono,
                email=email,
                torre=torre,
                tarjeta=tarjeta_obj,
                parqueadero=parqueadero,
                placa=placa,
                fecha=fecha,
                hora_registro=hora_registro,
                observaciones=observaciones
            )

            if tipo_usuario == "residente":
                return redirect("usuarios")
            else:
                return redirect("visitantes")

        except IntegrityError:
            return render(request, 'registroa/registroa.html', {
                'error': 'Error al registrar'
            })

    return render(request, 'registroa/registroa.html')

def ingresousu(request):
    return render(request, 'ingresousu/ingresousu.html')

def verusuario(request):
    
    query = request.GET.get('q', '')

    lista_registros = Registro.objects.all().order_by('-id')

    if query:
        lista_registros = lista_registros.filter(
            Q(nombre__icontains=query) |
            Q(documento__icontains=query)
        )

    paginator = Paginator(lista_registros, 8)

    page_number = request.GET.get('page')

    registros = paginator.get_page(page_number)

    pagina_actual = registros.number

    inicio = ((pagina_actual - 1) // 5) * 5 + 1

    fin = min(
        inicio + 4,
        paginator.num_pages
    )

    paginas = range(
        inicio,
        fin + 1
    )

    return render(
        request,
        'verusuario/verusuario.html',
        {
            'registros': registros,
            'query': query,
            'paginas': paginas
        }
    )

def eliminar(request):
    return render(request, 'eliminar/eliminar.html')

from django.shortcuts import render, redirect


def verdatosu(request, id):
    usuario = get_object_or_404(Registro, id=id)

    
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("usuarios")

    if request.method == 'POST':
        form = RegistroForm(request.POST, instance=usuario)
        # datos enviados por el usuario y indico que voy a editar para que no me guarde un nuevo usuario sino que se edite

        if form.is_valid():
            form.save()  # metodo para poder guardar los cambios en usuarios
            return redirect('usuarios')
        else:
            print(form.errors)  # debug para ver errores del formulario

    else:
        form = RegistroForm(instance=usuario)

    return render(request, 'verdatosu/verdatosu.html', {
        # Se crea el formulario con los datos del usuario para que aparezcan llenos y se puedan editar
        'form': form,  # Se envían esos datos al HTML para mostrarlos en la página
        'usuario': usuario
    })


def gestion(request):
    return render(request, 'gestion/gestion.html')


@login_required
def usuarios(request):
    
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")

    query = request.GET.get('q', '')

    lista_registros = Registro.objects.filter(
        tipo_usuario="residente"
    ).order_by('-id')

    if query:
        lista_registros = lista_registros.filter(
            Q(nombre__icontains=query) |
            Q(documento__icontains=query)
        )

    paginator = Paginator(lista_registros, 5)

    page_number = request.GET.get('page')

    registros = paginator.get_page(page_number)

    pagina_actual = registros.number

    inicio = ((pagina_actual - 1) // 5) * 5 + 1

    fin = min(
        inicio + 4,
        paginator.num_pages
    )

    paginas = range(
        inicio,
        fin + 1
    )

    return render(
        request,
        'usuarios/usuarios.html',
        {
            'registros': registros,
            'query': query,
            'paginas': paginas
        }
    )


def editarh(request):
    return render(request, 'editarh/editarh.html')





def generar_numero_tarjeta():
    ultimo = Tarjeta.objects.aggregate(Max("numero"))["numero__max"]
    return str(int(ultimo) + 1) if ultimo else "1000"



def detalle_tarjeta(request, id):

    registro = get_object_or_404(
        Registro.objects.select_related(
            "tarjeta"
        ).prefetch_related(
            "tarjeta__puertas"
        ),
        id=id
    )

    return render(
        request,
        "tarjetas/detalle_tarjeta.html",
        {
            "registro": registro
        }
    )



def tarjetas(request):
    
    print("USUARIO:", request.user)
    print("AUTENTICADO:", request.user.is_authenticated)
    print("GRUPOS:", list(request.user.groups.values_list("name", flat=True)))

    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
       
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")

    query = request.GET.get("buscar", "")
    estado = request.GET.get("estado", "")
    puerta = request.GET.get("puerta", "")

    registros_list = Registro.objects.select_related(
        "tarjeta"
    ).prefetch_related(
        "tarjeta__puertas"
    ).all().order_by("-id")

    # BUSCADOR
    if query:
        registros_list = registros_list.filter(
            Q(nombre__icontains=query) |
            Q(documento__icontains=query)
        )

    # FILTRO ESTADO
    if estado == "activa":
        registros_list = registros_list.filter(
            tarjeta__activa=True
        )

    elif estado == "inactiva":
        registros_list = registros_list.filter(
            tarjeta__activa=False
        )

    # FILTRO PUERTA
    if puerta:
        registros_list = registros_list.filter(
            tarjeta__puertas__id=puerta
        )

    registros_list = registros_list.distinct()

    # ESTADÍSTICAS
    total_tarjetas = Tarjeta.objects.count()

    tarjetas_activas = Tarjeta.objects.filter(
        activa=True
    ).count()

    tarjetas_inactivas = Tarjeta.objects.filter(
        activa=False
    ).count()

    # ACCIONES POST
    if request.method == "POST":

        print("POST RECIBIDO")

        accion = request.POST.get("accion")
        tarjeta_id = request.POST.get("tarjeta_id")

        print("ACCION:", accion)
        print("TARJETA:", tarjeta_id)

        # ACTIVAR / DESACTIVAR
        if accion == "cambiar_estado" and tarjeta_id:

            tarjeta = get_object_or_404(
                Tarjeta,
                id=tarjeta_id
            )

            if tarjeta.bloqueada:

                messages.error(
                    request,
                    "La tarjeta está bloqueada automáticamente por seguridad"
                )

                return redirect("tarjetas")

            registro = Registro.objects.filter(
                tarjeta=tarjeta
            ).first()

            if registro:

                HistorialTarjeta.objects.create(
                    registro=registro,
                    tarjeta=tarjeta,
                    accion="desactivada" if tarjeta.activa else "activada"
                )

            tarjeta.activa = not tarjeta.activa
            tarjeta.save()

            messages.success(
                request,
                "Estado de tarjeta actualizado correctamente"
            )

            return redirect("tarjetas")

        # CAMBIAR TARJETA
        elif accion == "cambiar_tarjeta" and tarjeta_id:

            tarjeta = get_object_or_404(
                Tarjeta,
                id=tarjeta_id
            )

            if tarjeta.bloqueada:

                messages.error(
                    request,
                    "No se puede cambiar una tarjeta bloqueada"
                )

                return redirect("tarjetas")

            registro = get_object_or_404(
                Registro,
                tarjeta=tarjeta
            )

            HistorialTarjeta.objects.create(
                registro=registro,
                tarjeta=tarjeta,
                accion="desactivada"
            )

            tarjeta.activa = False
            tarjeta.save()

            nueva_tarjeta = Tarjeta.objects.create(
                numero=generar_numero_tarjeta(),
                activa=True
            )

            puertas_ids = request.POST.getlist("puertas")

            if puertas_ids:
                nueva_tarjeta.puertas.set(
                    puertas_ids
                )

            registro.tarjeta = nueva_tarjeta
            registro.save()

            HistorialTarjeta.objects.create(
                registro=registro,
                tarjeta=nueva_tarjeta,
                accion="cambiada"
            )

            messages.success(
                request,
                "Nueva tarjeta generada correctamente"
            )

            return redirect("tarjetas")

    # PAGINACIÓN
    paginator = Paginator(registros_list, 5)

    page_number = request.GET.get("page")

    registros = paginator.get_page(page_number)

    pagina_actual = registros.number

    inicio = ((pagina_actual - 1) // 5) * 5 + 1

    fin = min(inicio + 4, paginator.num_pages)

    paginas = range(inicio, fin + 1)

    puertas = Puerta.objects.all()

    return render(
        request,
        "tarjetas/tarjetas.html",
        {
            "registros": registros,
            "buscar": query,
            "query": query,
            "estado": estado,
            "puerta": puerta,
            "puertas": puertas,
            "paginas": paginas,
            "total_tarjetas": total_tarjetas,
            "tarjetas_activas": tarjetas_activas,
            "tarjetas_inactivas": tarjetas_inactivas,
        }
    )

def asignartarjeta(request):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")

 
    query = request.GET.get("buscar", "")
    tarjeta_query = request.GET.get("tarjeta", "")
    estado = request.GET.get("estado", "")

    registros_list = Registro.objects.all().order_by("-id")

    # filtro por nombre o documento
    if query:
        registros_list = registros_list.filter(
            Q(nombre__icontains=query) |
            Q(documento__icontains=query)
        )

    # filtro por número de tarjeta
    if tarjeta_query:
        registros_list = registros_list.filter(
            tarjeta__numero__icontains=tarjeta_query
        )

    # filtro por estado (con/sin tarjeta)
    if estado == "con":
        registros_list = registros_list.filter(tarjeta__isnull=False)

    elif estado == "sin":
        registros_list = registros_list.filter(tarjeta__isnull=True)

    paginator = Paginator(registros_list, 5)
    page_number = request.GET.get("page")
    registros = paginator.get_page(page_number)

    pagina_actual = registros.number
    inicio = ((pagina_actual - 1) // 5) * 5 + 1
    fin = min(inicio + 4, paginator.num_pages)
    paginas = range(inicio, fin + 1)


    if request.method == "POST":
        accion = request.POST.get("accion")
        registro_id = request.POST.get("registro_id")

        if accion == "asignar" and registro_id:
            registro = get_object_or_404(Registro, id=registro_id)

            if registro.tarjeta:
                messages.error(request, "Este usuario ya tiene una tarjeta asignada")
                return redirect("asignartarjeta")

            nuevo_numero = (request.POST.get("nuevo_numero") or "").strip()

            if not nuevo_numero:
                messages.error(request, "Debe ingresar número de tarjeta")
                return redirect("asignartarjeta")

            if Tarjeta.objects.filter(numero=nuevo_numero).exists():
                messages.error(request, "La tarjeta ya ha sido asignada")
                return redirect("asignartarjeta")

            nueva_tarjeta = Tarjeta.objects.create(
                numero=nuevo_numero,
                activa=True
            )

            puertas_ids = request.POST.getlist("puertas")
            if puertas_ids:
                nueva_tarjeta.puertas.set(puertas_ids)

            registro.tarjeta = nueva_tarjeta
            registro.save()

            HistorialTarjeta.objects.create(
                registro=registro,
                tarjeta=nueva_tarjeta,
                accion="asignada"
            )

            messages.success(request, "Tarjeta asignada correctamente")
            return redirect("asignartarjeta")

    puertas = Puerta.objects.all()

 
    return render(request, "asignartarjeta/asignartarjeta.html", {
        "registros": registros,
        "query": query,
        "tarjeta_query": tarjeta_query,
        "estado": estado,
        "puertas": puertas,
        "paginas": paginas,
    })
def historialtarjeta(request):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")
    
    nombre = request.GET.get("nombre", "")
    tarjeta = request.GET.get("tarjeta", "")
    fecha = request.GET.get("fecha", "")

    historial_list = HistorialTarjeta.objects.select_related(
        "registro",
        "tarjeta"
    ).order_by("-fecha")

    # FILTRO NOMBRE
    if nombre:
        historial_list = historial_list.filter(
            registro__nombre__icontains=nombre
        )

    # FILTRO TARJETA
    if tarjeta:
        historial_list = historial_list.filter(
            tarjeta__numero__icontains=tarjeta
        )

    # FILTRO FECHA CORRECTO (RANGO)
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")

            fecha_inicio = fecha_obj
            fecha_fin = fecha_obj + timedelta(days=1)

            historial_list = historial_list.filter(
                fecha__gte=fecha_inicio,
                fecha__lt=fecha_fin
            )

        except ValueError:
            pass

    # PAGINACIÓN
    paginator = Paginator(historial_list, 10)
    page_number = request.GET.get("page")
    historial = paginator.get_page(page_number)

    # PAGINACIÓN POR BLOQUES
    pagina_actual = historial.number
    inicio = ((pagina_actual - 1) // 5) * 5 + 1
    fin = min(inicio + 4, paginator.num_pages)
    paginas = range(inicio, fin + 1)

    return render(
        request,
        "historialtarjeta/historialtarjeta.html",
        {
            "historial": historial,
            "nombre": nombre,
            "tarjeta": tarjeta,
            "fecha": fecha,
            "paginas": paginas,
        }
    )


def estado_legible(self):
    if self.accion == "activada":
        return "Tarjeta activa"
    elif self.accion == "desactivada":
        return "Tarjeta desactivada"
    return self.accion


def control(request):
    
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(
            request,
            "No tienes acceso a Direcciones IP"
        )
        return redirect("cliente")

    datos = Dispositivo.objects.select_related("puerta").all()

    return render(
        request,
        "control/control.html",
        {
            "datos": datos
        }
    )
def editart(request):
    return render(request, 'editart/editart.html')

def buscar(request):
    return render(request, 'buscar/buscar.html')

def editaracc(request):
    if not (
        request.user.groups.filter(name="Administrador").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("editaracc")
    datos = Dispositivo.objects.select_related("puerta").all()

    if request.method == "POST":
        ids = request.POST.getlist("id")

        for registro_id in ids:
            dispositivo = get_object_or_404(Dispositivo, id=registro_id)

            nombre_puerta = request.POST.get(f"puerta_{registro_id}")
            ip_valor = request.POST.get(f"ip_{registro_id}")

            estado = "activo" if f"estado_{registro_id}" in request.POST else "inactivo"

            try:
                puerta_obj = Puerta.objects.get(nombre=nombre_puerta)
            except Puerta.DoesNotExist:
                continue

            dispositivo.puerta = puerta_obj
            dispositivo.ip = ip_valor
            dispositivo.estado = estado
            dispositivo.save()

        return redirect("control")

    return render(request, "editaracc/editaracc.html", {"datos": datos})
def peatones(request):
    lista_registros = RegistroAcceso.objects.filter(tipo_acceso="conjunto", puerta="principal").order_by('-fecha', '-hora_entrada')

    paginator = Paginator(lista_registros, 5)  # 5 registros
    page_number = request.GET.get('page')
    registros = paginator.get_page(page_number)
    return render(request, 'peatones/peatones.html', {"registros": registros})

def emergencia(request):
    return render(request, 'emergencia/emergencia.html')

def discapacitados(request):
    lista_registros = RegistroAcceso.objects.filter(tipo_acceso="conjunto", puerta="discapacitados").order_by("-fecha","-hora_entrada")
    paginator = Paginator(lista_registros,5)
    page_number = request.GET.get("page")
    registros = paginator.get_page(page_number)
    return render(request, "discapacitados/discapacitados.html", {"registros": registros})

def vehiculos(request):
    lista_registros = RegistroAcceso.objects.filter(tipo_acceso="conjunto", puerta="vehiculos").order_by("-fecha","-hora_entrada")
    paginator = Paginator(lista_registros,5)
    page_number = request.GET.get("page")
    registros = paginator.get_page(page_number)


    return render(request, 'vehiculos/vehiculos.html' , {"registros": registros})


def recepcion(request):
    return render(request, 'recepcion/recepcion.html')

def puertas(request):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
        or request.user.groups.filter(name="Seguridad").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")
    puertas = Puerta.objects.all()
    return render(request, 'puertas/puertas.html', {"puertas": puertas})

from django.db.models import Q

def paquetes(request):
    
    #  PERMISOS
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
        or request.user.groups.filter(name="Seguridad").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")

    #  PARÁMETROS
    query = request.GET.get("q", "")
    fecha = request.GET.get("fecha", "")
    estado = request.GET.get("estado", "")

    # QUERY BASE
    queryset = Paquetes.objects.all().order_by("-id")

    
    if query:
        queryset = queryset.filter(
            Q(destinatario__icontains=query) |
            Q(documento__icontains=query) |
            Q(paquete__icontains=query) |
            Q(agencia__icontains=query)
        )

        # FILTRO DIFUSO (FUZZY SEARCH)
        resultados = []

        for p in queryset:
            texto = f"{p.destinatario} {p.documento} {p.paquete} {p.agencia}"

            similitud = difflib.SequenceMatcher(
                None,
                query.lower(),
                texto.lower()
            ).ratio()

            if similitud > 0.4:
                resultados.append(p.id)

        queryset = queryset.filter(id__in=resultados)

    # FILTRO POR FECHA
    if fecha:
        queryset = queryset.filter(fecha=fecha)

    #  FILTRO POR ESTADO
    if estado:
        queryset = queryset.filter(estado=estado)


    paginator = Paginator(queryset, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    current_page = page_obj.number
    start = ((current_page - 1) // 5) * 5 + 1
    end = min(start + 4, paginator.num_pages)
    paginas = range(start, end + 1)

    return render(
        request,
        "paquetes/paquetes.html",
        {
            "paquetes": page_obj,
            "query": query,
            "fecha": fecha,
            "estado": estado,
            "paginas": paginas,
        }
    )
def visitantes(request):
    
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")

    query = request.GET.get('q', '')

    lista_registros = Registro.objects.filter(
        tipo_usuario="visitante"
    ).order_by('-id')

    if query:
        lista_registros = lista_registros.filter(
            Q(nombre__icontains=query) |
            Q(documento__icontains=query)
        )

    paginator = Paginator(lista_registros, 5)

    page_number = request.GET.get('page')

    registros = paginator.get_page(page_number)

    pagina_actual = registros.number

    inicio = ((pagina_actual - 1) // 5) * 5 + 1

    fin = min(
        inicio + 4,
        paginator.num_pages
    )

    paginas = range(
        inicio,
        fin + 1
    )

    return render(
        request,
        'visitantes/visitantes.html',
        {
            'registros': registros,
            'query': query,
            'paginas': paginas
        }
    )

@login_required
def editarvisi(request, id):
    usuario = get_object_or_404(Registro, id=id)

    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("visitantes")

    config = get_config()

    if not config.edicion_usuarios:
        messages.error(request, "Edición deshabilitada")
        return redirect("visitantes")

    if request.method == 'POST':
        form = RegistroForm(request.POST, instance=usuario)
        # datos enviados por el usuario y indico que voy a editar para qur no me guarde un nuevo usuario si no que se edite

        if form.is_valid():
            form.save()  # metodo para poder guardar los cambios en usuarios
            return redirect('visitantes')

    else:
        form = RegistroForm(instance=usuario)

    return render(request, 'editarvisi/editarvisi.html', {
        # Se crea el formulario con los datos del usuario para que aparezcan llenos y se puedan editar
        'form': form,  # Se envían esos datos al HTML para mostrarlos en la página
        'usuario': usuario
    })


def editarpa(request, id):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")
    paquete = get_object_or_404(Paquetes, id=id)

    if request.method == 'POST':
        form = PaquetesForm(request.POST, instance=paquete)
        if form.is_valid():
            form.save()
            return redirect('paquetes')
    else:
        form = PaquetesForm(instance=paquete)

    return render(request, 'editarpa/editarpa.html', {
        'form': form,
        'paquete': paquete
    })
    

def configuracion(request):
    return render(request, 'configuracion/configuracion.html')

def editarvehi(request):
    return render(request, 'editarvehi/editarvehi.html')

def mensajeria(request):
    if request.method == "POST":
        documento = request.POST.get("documento")

        registro = Registro.objects.filter(documento=documento).first()

        if registro:
            destinatario = registro.nombre
            torre = registro.torre
        else:
            destinatario = request.POST.get("destinatario")
            torre = request.POST.get("torre")

            if not destinatario:
                return render(request, 'mensajeria/mensajeria.html', {
                    'error': 'Debe ingresar el nombre del destinatario'
                })

        Paquetes.objects.create(
            documento=documento,
            destinatario=destinatario,
            nombre_recibe=request.POST.get("nombre_recibe"),
            torre=torre,
            paquete=request.POST.get("paquete"),
            agencia=request.POST.get("agencia"),
            fecha=request.POST.get("fecha"),
            hora_ingreso=request.POST.get("hora_ingreso"),
            hora_entrega=request.POST.get("hora_entrega") or None,
            observaciones=request.POST.get("observaciones") or None
        )

        messages.success(request, "Paquete registrado correctamente")
        return redirect("paquetes")

    return render(request, 'mensajeria/mensajeria.html')


def torres(request):
    lista_registros = RegistroAcceso.objects.filter(
        tipo_acceso="torre"
    ).order_by("-fecha", "-hora_entrada")

    paginator = Paginator(lista_registros, 5)
    page_number = request.GET.get("page")
    registros = paginator.get_page(page_number)

    return render(request, "torres/torres.html", {"registros": registros})


def ip(request):
    
    if not request.user.groups.filter(name="Administrador").exists():
        messages.error(
            request,
            "No tienes acceso a Direcciones IP"
        )
        return redirect("cliente")

    if request.method == "POST":

        nombre_puerta = request.POST.get("puerta").strip()
        ip_valor = request.POST.get("ip")
        estado = request.POST.get("estado")

        puerta_obj, _ = Puerta.objects.get_or_create(
            nombre=nombre_puerta
        )

        Dispositivo.objects.update_or_create(
            puerta=puerta_obj,
            defaults={
                "ip": ip_valor,
                "estado": estado
            }
        )

        return redirect("control")

    return render(request, "ip/ip.html")

def limpiar_texto(texto):
    if not texto:
        return ""

    texto = str(texto).lower().strip()

    # eliminar palabras innecesarias comunes en búsquedas
    palabras = ["puerta", "acceso", "al", "la", "el"]
    for p in palabras:
        texto = texto.replace(p, "")

    return texto.strip()


def historialacceso(request):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
        or request.user.groups.filter(name="Seguridad").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")
    
    persona = request.GET.get("persona", "")
    torre = request.GET.get("torre", "")
    fecha = request.GET.get("fecha", "")
    puerta = request.GET.get("puerta", "")


    # EVITAR NONE

    if persona == "None":
        persona = ""

    if torre == "None":
        torre = ""

    if fecha == "None":
        fecha = ""

    if puerta == "None":
        puerta = ""

  
    # CONSULTA BASE

    lista = RegistroAcceso.objects.select_related(
        "persona",
        "persona__tarjeta"
    ).order_by(
        "-fecha",
        "-hora_entrada"
    )


    # FILTRO PERSONA

    if persona:

        lista = lista.filter(
            Q(persona__nombre__icontains=persona) |
            Q(persona__documento__icontains=persona)
        )


    # FILTRO TORRE

    if torre:

        torre = torre.lower().replace(" ", "")

        if "torre" in torre:

            numero = "".join(
                filter(str.isdigit, torre)
            )

            if numero:
                torre = f"torre_{numero}"

        lista = lista.filter(
            torre__icontains=torre
        )


    # FILTRO FECHA

    if fecha:

        lista = lista.filter(
            fecha=fecha
        )


    # FILTRO PUERTA

    if puerta:

        try:

            puerta_limpia = limpiar_texto(puerta)

        except:

            puerta_limpia = puerta

        lista = lista.filter(
            Q(puerta__icontains=puerta_limpia) |
            Q(tipo_acceso__icontains=puerta_limpia)
        )


    for acceso in lista:

        acceso.tarjeta_bloqueada = False

        if acceso.persona:

            try:

                if acceso.persona.tarjeta:

                    acceso.tarjeta_bloqueada = (
                        acceso.persona.tarjeta.bloqueada
                    )

            except:

                acceso.tarjeta_bloqueada = False

    paginator = Paginator(lista, 6)

    page_number = request.GET.get("page")

    registros = paginator.get_page(page_number)
    
    pagina_actual = registros.number

    inicio = ((pagina_actual - 1) // 5) * 5 + 1
    
    fin = min(
        inicio + 4,
        paginator.num_pages
    )

    paginas = range(inicio,fin + 1)


    return render(
        request,
        "historialacceso/historialacceso.html",
        {
            "registros": registros,
            "paginas": paginas,
            "persona": persona,
            "torre": torre,
            "fecha": fecha,
            "puerta": puerta
        }
    )
    
def cliente(request):
    total_usuarios = Registro.objects.count()
    tarjetas_activas = Tarjeta.objects.filter(activa=True).count()
    accesos_hoy = RegistroAcceso.objects.filter(fecha=date.today()).count()

    return render(request, 'cliente/cliente.html', {
        'total_usuarios': total_usuarios,
        'tarjetas_activas': tarjetas_activas,
        'accesos_hoy': accesos_hoy
    })
    
def link_callback(uri, rel):
    
    result = finders.find(uri)

    if result:

        if not isinstance(result, (list, tuple)):
            result = [result]

        result = list(
            os.path.realpath(path)
            for path in result
        )

        path = result[0]

    else:

        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT

        if uri.startswith(sUrl):

            path = os.path.join(
                sRoot,
                uri.replace(sUrl, "")
            )

        else:
            return uri

    return path


def link_callback(uri, rel):
    
    result = finders.find(uri)

    if result:
        path = os.path.abspath(result)
    else:
        path = os.path.join(settings.BASE_DIR, uri)

    if not os.path.isfile(path):
        raise Exception(f"Archivo no encontrado: {path}")

    return path


def reporte_historial_pdf(request):
    
    persona = request.GET.get("persona")
    torre = request.GET.get("torre")
    fecha = request.GET.get("fecha")
    puerta = request.GET.get("puerta")
    email_destino = request.GET.get("email")

    registros_qs = RegistroAcceso.objects.select_related("persona").order_by(
        "-fecha",
        "-hora_entrada"
    )

    # limpiar valores basura
    def limpiar(v):
        if v in [None, "", "None"]:
            return None
        return v

    persona = limpiar(persona)
    torre = limpiar(torre)
    fecha = limpiar(fecha)
    puerta = limpiar(puerta)


    # FILTRO PERSONA

    if persona:
        registros_qs = registros_qs.filter(
            Q(persona__nombre__icontains=persona) |
            Q(persona__documento__icontains=persona)
        )

    # FILTRO TORRE 

    if torre:

        torre = torre.lower().replace(" ", "")

        if "torre" in torre:
            numero = "".join(filter(str.isdigit, torre))
            if numero:
                torre = f"torre_{numero}"

        registros_qs = registros_qs.filter(
            torre__icontains=torre
        )


    # FILTRO FECHA

    if fecha:
        registros_qs = registros_qs.filter(fecha=fecha)


    # FILTRO PUERTA 

    if puerta:

        puerta_limpia = limpiar_texto(puerta)

        registros_qs = registros_qs.filter(
            Q(puerta__icontains=puerta_limpia) |
            Q(tipo_acceso__icontains=puerta_limpia)
        )


    # ARMAR DATA PARA PDF

    registros = []

    for r in registros_qs:
        registros.append({
            "id": r.id or "-",
            "persona": r.persona.nombre if r.persona else "-",
            "fecha": str(r.fecha) if r.fecha else "-",
            "hora_entrada": str(r.hora_entrada) if r.hora_entrada else "-",
            "hora_salida": str(r.hora_salida) if r.hora_salida else "-",
            "puerta": r.puerta or "-",
            "estado": r.estado or "-"
        })

    fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template = get_template("pdf/historial_pdf.html")

    html = template.render({
        "registros": registros,
        "fecha_reporte": fecha_reporte
    })

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="historial.pdf"'

    pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback
    )

    if email_destino:

        email = EmailMessage(
            subject="Reporte historial",
            body="Adjunto encontrarás el reporte PDF.",
            from_email=settings.EMAIL_HOST_USER,
            to=[email_destino],
        )

        email.attach(
            "historial.pdf",
            response.content,
            "application/pdf"
        )

        email.send()

    return response
def imprimir(request):
    persona = request.GET.get("persona")
    torre = request.GET.get("torre")
    fecha = request.GET.get("fecha")
    puerta = request.GET.get("puerta")

    registros_qs = RegistroAcceso.objects.select_related("persona").order_by(
        "-fecha", "-hora_entrada"
    )

    if persona:
        registros_qs = registros_qs.filter(
            Q(persona__nombre__icontains=persona) |
            Q(persona__documento__icontains=persona)
        )

    if torre:
        registros_qs = registros_qs.filter(torre__icontains=torre)

    if fecha:
        registros_qs = registros_qs.filter(fecha=fecha)

    if puerta:
        registros_qs = registros_qs.filter(puerta__icontains=puerta)

    fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render(request, "imprimir/imprimir.html", {
        "registros": registros_qs,
        "fecha_reporte": fecha_reporte
    })
    
def pdfusuarios(request):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()

    ):
        messages.error(request, "No tienes permisos")
        return redirect("pdfusuarios")
    
    email_destino = request.GET.get("email")

    registros_qs = Registro.objects.all().order_by("-id")

    registros = []

    for r in registros_qs:
        registros.append({
            "tipo_usuario": r.tipo_usuario or "-",
            "nombre": r.nombre or "-",
            "documento": r.documento or "-",
            "telefono": r.telefono or "-",
            "email": r.email or "-",
            "torre": r.torre or "-",
            "tarjeta": r.tarjeta.numero if r.tarjeta else "-",
            "parqueadero": r.parqueadero or "-",
            "placa": r.placa or "-",
            "fecha": str(r.fecha) if r.fecha else "-",
            "hora_registro": str(r.hora_registro) if r.hora_registro else "-",
        })

    fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template = get_template("pdfusuarios/pdfusuarios.html")

    html = template.render({
        "registros": registros,
        "fecha_reporte": fecha_reporte
    })

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="usuarios.pdf"'

    pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback
    )

    if email_destino:

        email = EmailMessage(
            subject="Reporte de usuarios",
            body="Adjunto encontrarás el reporte PDF de usuarios registrados.",
            from_email=settings.EMAIL_HOST_USER,
            to=[email_destino],
        )

        email.attach(
            "usuarios.pdf",
            response.content,
            "application/pdf"
        )

        email.send()

    return response

def pdfpaquetes(request):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()

    ):
        messages.error(request, "No tienes permisos")
        return redirect("pdfpaquetes")
    
    email_destino = request.GET.get("email")

    paquetes_qs = Paquetes.objects.all().order_by("-id")

    paquetes = []

    for p in paquetes_qs:

        paquetes.append({

            "destinatario": p.destinatario or "-",
            "documento": p.documento or "-",
            "nombre_recibe": p.nombre_recibe or "-",
            "torre": p.torre or "-",
            "paquete": p.paquete or "-",
            "agencia": p.agencia or "-",
            "fecha": str(p.fecha) if p.fecha else "-",
            "hora_ingreso": str(p.hora_ingreso) if p.hora_ingreso else "-",
            "hora_entrega": str(p.hora_entrega) if p.hora_entrega else "-",
            "observaciones": p.observaciones or "-",

        })

    fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template = get_template("pdfpaquetes/pdfpaquetes.html")

    html = template.render({

        "paquetes": paquetes,
        "fecha_reporte": fecha_reporte

    })

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = (
        'attachment; filename="paquetes.pdf"'
    )

    pisa.CreatePDF(

        html,
        dest=response,
        link_callback=link_callback

    )

    if email_destino:

        email = EmailMessage(

            subject="Reporte de paquetes",
            body="Adjunto encontrarás el reporte PDF de paquetes.",

            from_email=settings.EMAIL_HOST_USER,

            to=[email_destino],

        )

        email.attach(

            "paquetes.pdf",
            response.content,
            "application/pdf"

        )

        email.send()

    return response



def pdfhistorialtarjeta(request):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("historialtarjeta")
    
    nombre = request.GET.get("nombre")
    tarjeta = request.GET.get("tarjeta")
    fecha = request.GET.get("fecha")
    email_destino = request.GET.get("email")

    historial_qs = HistorialTarjeta.objects.select_related(
        "registro",
        "tarjeta"
    ).order_by("-fecha")

    def limpiar(v):
        if v in [None, "", "None"]:
            return None
        return v

    nombre = limpiar(nombre)
    tarjeta = limpiar(tarjeta)
    fecha = limpiar(fecha)

    # FILTRO NOMBRE
    if nombre:
        historial_qs = historial_qs.filter(
            Q(registro__nombre__icontains=nombre) |
            Q(registro__documento__icontains=nombre)
        )

    # FILTRO TARJETA
    if tarjeta:
        historial_qs = historial_qs.filter(
            tarjeta__numero__icontains=tarjeta
        )

    #FILTRO FECHA 
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")

            fecha_inicio = fecha_obj
            fecha_fin = fecha_obj + timedelta(days=1)

            historial_qs = historial_qs.filter(
                fecha__gte=fecha_inicio,
                fecha__lt=fecha_fin
            )

        except ValueError:
            pass

    historial = []

    for h in historial_qs:
        historial.append({
            "id": h.id or "-",
            "nombre": h.registro.nombre if h.registro else "-",
            "tarjeta": h.tarjeta.numero if h.tarjeta else "-",
            "estado": h.estado_legible,
            "fecha": h.fecha.strftime("%d/%m/%Y %H:%M") if h.fecha else "-"
        })

    fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template = get_template(
        "pdfhistorialtarjeta/pdfhistorialtarjeta.html"
    )

    html = template.render({
        "historial": historial,
        "fecha_reporte": fecha_reporte
    })

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = (
        'attachment; filename="historial_tarjetas.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback
    )

    # ENVÍO POR EMAIL
    if email_destino:
        email = EmailMessage(
            subject="Reporte historial de tarjetas",
            body="Adjunto encontrarás el reporte PDF del historial de tarjetas.",
            from_email=settings.EMAIL_HOST_USER,
            to=[email_destino],
        )

        email.attach(
            "historial_tarjetas.pdf",
            response.content,
            "application/pdf"
        )

        email.send()

    return response

def pdfingresos(request):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()

    ):
        messages.error(request, "No tienes permisos")
        return redirect("pdfingresos")
    
    email_destino = request.GET.get("email")

    ingresos_qs = Ingreso.objects.all().order_by("-id")

    ingresos = []

    for i in ingresos_qs:

        ingresos.append({

            "tipo_ingreso": i.tipo_ingreso or "-",
            "nombre": i.nombre or "-",
            "tipo_documento": i.tipo_documento or "-",
            "documento": i.documento or "-",
            "visita_a": i.visita_a or "-",
            "placa": i.placa or "-",
            "empresa": i.empresa or "-",
            "hora_ingreso": str(i.hora_ingreso) if i.hora_ingreso else "-",
            "hora_salida": str(i.hora_salida) if i.hora_salida else "-",
            "estado": i.estado or "-",
            "observaciones": i.observaciones or "-",

        })

    fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template = get_template("pdfingresos/pdfingresos.html")

    html = template.render({

        "registros": ingresos,
        "fecha_reporte": fecha_reporte

    })

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = 'attachment; filename="ingresos.pdf"'

    pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback
    )

    if email_destino:

        email = EmailMessage(

            subject="Reporte de ingresos",
            body="Adjunto encontrarás el reporte PDF de ingresos.",

            from_email=settings.EMAIL_HOST_USER,

            to=[email_destino],

        )

        email.attach(
            "ingresos.pdf",
            response.content,
            "application/pdf"
        )

        email.send()

    return response


def visitantestem(request):
    
    if request.method == "POST":

        Ingreso.objects.create(

            tipo_ingreso=request.POST.get("tipo_ingreso"),
            nombre=request.POST.get("nombre"),
            tipo_documento=request.POST.get("tipo_documento"),
            documento=request.POST.get("documento"),
            visita_a=request.POST.get("visita_a"),
            placa=request.POST.get("placa"),
            empresa=request.POST.get("empresa"),
            fecha=request.POST.get("fecha"),
            hora_ingreso=request.POST.get("hora_ingreso"),
            estado="Dentro",
            observaciones=request.POST.get("observaciones")

        )

        return redirect("listaingresos")

    return render(request, "visitantestem/visitantestem.html")

def listaingresos(request):
    
    query = request.GET.get("q", "")
    estado = request.GET.get("estado", "")
    fecha = request.GET.get("fecha", "")

    lista_registros = Ingreso.objects.all().order_by("-id")

    if query:
        lista_registros = lista_registros.filter(
            Q(nombre__icontains=query) |
            Q(documento__icontains=query) |
            Q(visita_a__icontains=query) |
            Q(empresa__icontains=query)
        )

    if estado:
        lista_registros = lista_registros.filter(estado=estado)

    if fecha:
        lista_registros = lista_registros.filter(fecha=fecha)

    paginator = Paginator(lista_registros, 5)
    page_number = request.GET.get("page")
    registros = paginator.get_page(page_number)

    return render(request, "listaingresos/listaingresos.html", {
        "registros": registros,
        "query": query,
        "estado": estado,
        "fecha": fecha
    })
    
def registrar_salida(request, id):
    
    visitante = get_object_or_404(Ingreso, id=id)

    visitante.hora_salida = datetime.now().time()
    visitante.estado = "Fuera"
    visitante.save()

    return redirect("listaingresos")

@login_required
def editar_ingreso(request, id):

    ingreso = get_object_or_404(Ingreso, id=id)

    if request.method == "POST":

        form = IngresoForm(request.POST, instance=ingreso)

        if form.is_valid():

            form.save()

            return redirect("listaingresos")

    else:

        form = IngresoForm(instance=ingreso)

    return render(

        request,

        "editar_ingreso/editar_ingreso.html",

        {
            "form": form,
            "ingreso": ingreso
        }

    )
    
    
@login_required
def registrar_entrega(request, id):
    if not (
        request.user.groups.filter(name="Administrador").exists()
        or request.user.groups.filter(name="Supervisor").exists()
        or request.user.groups.filter(name="Seguridad").exists()
    ):
        messages.error(request, "No tienes permisos")
        return redirect("cliente")

    paquete = get_object_or_404(
        Paquetes,
        id=id
    )
    paquete.estado = "Entregado"
    paquete.hora_entrega = datetime.now().time()
    paquete.entregado_por = request.user
    paquete.save()

    return redirect("paquetes")

def reporte_tarjetas_pdf(request):
    
    query = request.GET.get("buscar")
    estado = request.GET.get("estado")
    puerta = request.GET.get("puerta")
    email_destino = request.GET.get("email")

    registros_qs = Registro.objects.select_related(
        "tarjeta"
    ).prefetch_related(
        "tarjeta__puertas"
    ).order_by("-id")

    if query:

        registros_qs = registros_qs.filter(
            Q(nombre__icontains=query) |
            Q(documento__icontains=query)
        )

    if estado == "activa":

        registros_qs = registros_qs.filter(
            tarjeta__activa=True
        )

    elif estado == "inactiva":

        registros_qs = registros_qs.filter(
            tarjeta__activa=False
        )

    if puerta:

        registros_qs = registros_qs.filter(
            tarjeta__puertas__id=puerta
        )

    registros = []

    for r in registros_qs:

        puertas = ", ".join(
            [p.nombre for p in r.tarjeta.puertas.all()]
        ) if r.tarjeta else "Sin puertas"

        registros.append({

            "nombre": r.nombre,
            "documento": r.documento,
            "tarjeta": r.tarjeta.numero if r.tarjeta else "Sin tarjeta",
            "puertas": puertas,
            "estado": "Activa" if r.tarjeta and r.tarjeta.activa else "Inactiva"

        })

    fecha_reporte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    template = get_template(
        "reporte_tarjetas_pdf/reporte_tarjetas_pdf.html"
    )

    html = template.render({

        "registros": registros,
        "fecha_reporte": fecha_reporte

    })

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="gestion_tarjetas.pdf"'
    )

    pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback
    )

    if email_destino:

        email = EmailMessage(

            subject="Reporte gestión tarjetas",

            body="Adjunto encontrarás el reporte PDF.",

            from_email=settings.EMAIL_HOST_USER,

            to=[email_destino],

        )

        email.attach(
            "gestion_tarjetas.pdf",
            response.content,
            "application/pdf"
        )

        email.send()

    return response

@login_required
def ajustes(request):

    # SOLO ADMINISTRADOR
    if not request.user.groups.filter(name="Administrador").exists():

        messages.error(
            request,
            "No tienes permisos para acceder a configuración"
        )

        return redirect("cliente")

    # CONFIGURACIÓN GLOBAL
    configuracion, created = ConfiguracionSistema.objects.get_or_create(id=1)

    if request.method == "POST":


        boolean_fields = [
            "bloqueo_automatico",
            "verificacion_adicional",
            "alertas_correo",
            "alertas_sonoras",
            "actividad_sospechosa",
            "guardar_historial",
            "actividad_nocturna",
            "modo_oscuro"
        ]

        for field in boolean_fields:
            setattr(configuracion, field, field in request.POST)



        configuracion.cierre_automatico = request.POST.get(
            "cierre_automatico"
        )

        configuracion.tiempo_almacenamiento = request.POST.get(
            "tiempo_almacenamiento"
        )

        configuracion.rol_principal = request.POST.get("rol_principal") or configuracion.rol_principal or "Administrador"

        configuracion.save()


        hoy = timezone.now().date()

        if configuracion.tiempo_almacenamiento == "3 meses":

            fecha_limite = hoy - timedelta(days=90)

        elif configuracion.tiempo_almacenamiento == "6 meses":

            fecha_limite = hoy - timedelta(days=180)

        elif configuracion.tiempo_almacenamiento == "1 año":

            fecha_limite = hoy - timedelta(days=365)

        else:

            fecha_limite = None

        if fecha_limite:

            RegistroAcceso.objects.filter(
                fecha__lt=fecha_limite
            ).delete()



        RegistroAcceso.objects.create(
            persona=None,
            tipo_acceso="sistema",
            estado="configuracion_actualizada",
            motivo=f"Configuración modificada por {request.user.username}"
        )



        if (
            configuracion.actividad_sospechosa
            or configuracion.bloqueo_automatico
        ):

            Alerta.objects.create(
                tipo="INFO",
                mensaje="Se actualizaron reglas de seguridad del sistema",
                usuario=request.user
            )


        if configuracion.alertas_correo:

            try:

                send_mail(
                    "🚨 Alerta de Seguridad - Diamond Security",
                    f"""
Se detectó una modificación en la configuración del sistema.

Usuario: {request.user.username}

Configuraciones actuales:

• Bloqueo automático: {'Sí' if configuracion.bloqueo_automatico else 'No'}
• Verificación adicional: {'Sí' if configuracion.verificacion_adicional else 'No'}
• Actividad sospechosa: {'Sí' if configuracion.actividad_sospechosa else 'No'}

Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M')}

Este mensaje fue generado automáticamente por Diamond Security.
""",
                    "diamondsecurity3@gmail.com",
                    ["diamondsecurity3@gmail.com"],
                    fail_silently=False
                )

            except Exception as e:

                print("Error enviando correo:", e)

        messages.success(
            request,
            "Configuración actualizada correctamente"
        )

        return redirect("ajustes")

    return render(
        request,
        "ajustes/ajustes.html",
        {
            "configuracion": configuracion
        }
    )


  
class AtencionClienteViewSet(viewsets.ModelViewSet):
    queryset = AtencionCliente.objects.all()
    serializer_class = AtencionClienteSerializer


from django.contrib import messages

def apertura_emergencia(request):

    if not request.user.groups.filter(
        name__in=["Administrador", "Supervisor", "Seguridad"]
    ).exists():
        messages.error(request, "No tienes permisos")
        return redirect("cliente")

    if request.method == "POST":

        Puerta.objects.all().update(
            estado=True,
            emergencia=True
        )

        messages.warning(
            request,
            "MODO EMERGENCIA ACTIVADO"
        )

    return redirect("puertas")


def detener_emergencia(request):
    if request.method == "POST":

        Puerta.objects.all().update(
            emergencia=False
        )

        messages.success(request, "Modo emergencia desactivado")

    return redirect("puertas")


def cerrar_puertas(request):
    if request.method == "POST":

        Puerta.objects.all().update(
            estado=False,
            emergencia=False
        )

        messages.info(request, "Puertas cerradas correctamente")

    return redirect("puertas")
def cerrar_sesion(request):
    logout(request)
    return redirect("principal")