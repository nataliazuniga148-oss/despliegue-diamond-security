from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q, Max
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
            return render(request, "diamond/restablecer.html", {
                "error": "Las contraseñas no coinciden",
                "token": token_obj
            })

        try:
            validate_password(password1, user=token_obj.user)
        except ValidationError as e:
            return render(request, "diamond/restablecer.html", {
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

    return render(request, "diamond/restablecer.html", {
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


@api_view(["POST"])  #función de vista API
def registrar_acceso(request):  #lee los datos
    tarjeta = request.data.get("tarjeta")
    tipo_acceso = request.data.get("tipo_acceso")
    torre = request.data.get("torre")

    # normalizar torre
    if torre:

        torre = str(torre).lower().strip()

        # extraer solo números
        numero_torre = "".join(filter(str.isdigit, torre))

        if numero_torre:
            torre = f"torre_{numero_torre}"

    #validar datos básicos
    if not tarjeta:

        # REGISTRAR ACCESO DENEGADO
        RegistroAcceso.objects.create(
            persona=None,
            tipo_acceso="conjunto",
            torre=torre if torre else None,
            puerta="principal",
            estado="denegado"
        )

        return Response({"error": "Debe enviar la tarjeta"}, status=400)

    if not tipo_acceso:

        # REGISTRAR ACCESO DENEGADO
        RegistroAcceso.objects.create(
            persona=None,
            tipo_acceso="conjunto",
            torre=torre if torre else None,
            puerta="principal",
            estado="denegado"
        )

        return Response({"error": "Debe enviar el tipo de acceso"}, status=400)

    try:  #verificar que la tarjeta enviada por la solicitud exista en la tabla

        persona = Registro.objects.get(
            tarjeta__numero=tarjeta,
            tarjeta__activa=True
        )

        tarjeta_obj = persona.tarjeta

        # obtener IP automáticamente (no se recibe puerta desde el cliente)
        ip_cliente = obtener_ip(request)

        if not ip_cliente:

            # REGISTRAR ACCESO DENEGADO
            RegistroAcceso.objects.create(
                persona=persona,
                tipo_acceso=tipo_acceso,
                torre=torre if torre else None,
                puerta="principal",
                estado="denegado"
            )

            return Response({"error": "No se pudo obtener la IP"}, status=400)

        # soporte para desarrollo (localhost)
        posibles_ips = [ip_cliente]

        if ip_cliente == "127.0.0.1":
            posibles_ips.append("::1")

        elif ip_cliente == "::1":
            posibles_ips.append("127.0.0.1")

        try:

            dispositivo = Dispositivo.objects.select_related("puerta").get(
                ip__in=posibles_ips,
                estado="activo"
            )

            puerta_obj = dispositivo.puerta

        except Dispositivo.DoesNotExist:

            # REGISTRAR ACCESO DENEGADO
            RegistroAcceso.objects.create(
                persona=persona,
                tipo_acceso=tipo_acceso,
                torre=torre if torre else None,
                puerta="principal",
                estado="denegado"
            )

            return Response({
                "error": "Dispositivo no autorizado o inactivo"
            }, status=403)

        except Dispositivo.MultipleObjectsReturned:

            # REGISTRAR ACCESO DENEGADO
            RegistroAcceso.objects.create(
                persona=persona,
                tipo_acceso=tipo_acceso,
                torre=torre if torre else None,
                puerta="principal",
                estado="denegado"
            )

            return Response({
                "error": "Configuración duplicada de dispositivos"
            }, status=500)

        #validación extra por seguridad
        if not puerta_obj:

            # REGISTRAR ACCESO DENEGADO
            RegistroAcceso.objects.create(
                persona=persona,
                tipo_acceso=tipo_acceso,
                torre=torre if torre else None,
                puerta="principal",
                estado="denegado"
            )

            return Response({"error": "Puerta no configurada"}, status=500)

        # MODO EMERGENCIA (SE SALTA TODAS LAS VALIDACIONES)
        if puerta_obj.emergencia:

            acceso = RegistroAcceso.objects.create(
                persona=persona,
                tipo_acceso="conjunto",
                puerta=puerta_obj.tipo,
                estado="permitido"
            )

            serializer = RegistroAccesoSerializer(acceso)

            return Response(serializer.data, status=201)

        #validación de acceso a puerta
        if tipo_acceso == "conjunto":

            # verificar permiso a la puerta
            if not tarjeta_obj.puertas.filter(id=puerta_obj.id).exists():

                # REGISTRAR ACCESO DENEGADO
                RegistroAcceso.objects.create(
                    persona=persona,
                    tipo_acceso=tipo_acceso,
                    puerta=puerta_obj.tipo,
                    estado="denegado"
                )

                return Response({
                    "error": "Acceso denegado a esta puerta"
                }, status=403)

            puerta_registro = puerta_obj.tipo
            torre_registro = None

        #validación básica de torre
        elif tipo_acceso == "torre":

            if not torre:

                # REGISTRAR ACCESO DENEGADO
                RegistroAcceso.objects.create(
                    persona=persona,
                    tipo_acceso=tipo_acceso,
                    torre="torre_1",
                    estado="denegado"
                )

                return Response({
                    "error": "Debe enviar la torre"
                }, status=400)

            # normalizar torre BD
            torre_bd = str(persona.torre).lower().replace(" ", "")

            numero_bd = "".join(filter(str.isdigit, torre_bd))

            torre_bd = f"torre_{numero_bd}"

            # validar acceso torre
            if torre_bd != torre:

                # REGISTRAR ACCESO DENEGADO
                RegistroAcceso.objects.create(
                    persona=persona,
                    tipo_acceso=tipo_acceso,
                    torre=torre,
                    estado="denegado"
                )

                return Response({
                    "error": "Acceso denegado a esta torre"
                }, status=403)

            puerta_registro = None
            torre_registro = torre

        #validación parqueadero
        elif tipo_acceso == "parqueadero":

            # verificar que tenga parqueadero asignado
            if not persona.parqueadero:

                # REGISTRAR ACCESO DENEGADO
                RegistroAcceso.objects.create(
                    persona=persona,
                    tipo_acceso=tipo_acceso,
                    puerta="parqueadero",
                    estado="denegado"
                )

                return Response({
                    "error": "Usuario sin parqueadero asignado"
                }, status=403)

            # normalizar parqueadero BD
            parqueadero_bd = "".join(
                filter(str.isdigit, str(persona.parqueadero))
            )

            puerta_registro = f"Parqueadero {parqueadero_bd}"
            torre_registro = None

        else:

            # REGISTRAR ACCESO DENEGADO
            RegistroAcceso.objects.create(
                persona=None,
                tipo_acceso="conjunto",
                torre=torre if torre else None,
                puerta="principal",
                estado="denegado"
            )

            return Response({
                "error": "Tipo de acceso inválido"
            }, status=400)

        # salida o entrada
        if tipo_acceso == "torre":

            acceso_abierto = RegistroAcceso.objects.filter(
                persona=persona,
                torre=torre,
                estado="permitido",
                hora_salida__isnull=True
            ).last()

        elif tipo_acceso == "parqueadero":

            acceso_abierto = RegistroAcceso.objects.filter(
                persona=persona,
                tipo_acceso="parqueadero",
                estado="permitido",
                hora_salida__isnull=True
            ).last()

        else:

            acceso_abierto = RegistroAcceso.objects.filter(
                persona=persona,
                estado="permitido",
                hora_salida__isnull=True
            ).last()

        # SI YA TIENE ENTRADA ABIERTA = REGISTRAR SALIDA
        if acceso_abierto:

            acceso_abierto.hora_salida = datetime.now().time()
            acceso_abierto.save()

            return Response({
                "mensaje": "Salida registrada",
                "hora_salida": acceso_abierto.hora_salida
            }, status=200)

        # CREA NUEVA ENTRADA
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

        # REGISTRAR ACCESO DENEGADO
        RegistroAcceso.objects.create(
            persona=None,
            tipo_acceso="conjunto",
            torre=torre if torre else None,
            puerta="principal",
            estado="denegado"
        )

        return Response({
            "error": "Tarjeta no registrada o inactiva"
        }, status=404)
class AtencionClienteViewSet(viewsets.ModelViewSet):
    queryset = AtencionCliente.objects.all()
    serializer_class = AtencionClienteSerializer
    
def apertura_emergencia(request):
    if request.method == "POST":
        Puerta.objects.all().update(
            estado=True,
            emergencia=True
        )
        messages.warning(request, " MODO EMERGENCIA ACTIVADO")
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

def logeo(request):
    return render(request, 'usuarios/logeo.html')

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
    if request.method == "POST":#metodo POST para guardar la infortmación y verificar la informacion enviada por el usuario
        nombre = request.POST.get("nombre")
        documento = request.POST.get("numero_documento")
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
        mensaje = request.POST.get("mensaje")
        
        Solicitud.objects.create(
            nombre = nombre,
            correo = correo,
            tipo = tipo,
            mensaje = mensaje
        )
        messages.success(request, "Los datos han sido enviados correctamente.")
        return redirect("integraciones")
    
    return render(request, 'integraciones/integraciones.html')



def admin(request):
    return render(request, 'admin/admin.html')

def horarioad(request):
    return render(request, 'horarioad/horarioad.html')

def informes(request):
    return render(request, 'informes/informes.html')


def registroa(request):
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
        hora_ingreso = request.POST.get("hora_ingreso")
        hora_salida = request.POST.get("hora_salida") or None
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
                hora_ingreso=hora_ingreso,
                hora_salida=hora_salida,
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
    lista_registros = Registro.objects.all().order_by('-id')

    paginator = Paginator(lista_registros, 8)
    page_number = request.GET.get('page')
    registros = paginator.get_page(page_number)
    return render(request, 'verusuario/verusuario.html', {
        'registros': registros
    })



def eliminar(request):
    return render(request, 'eliminar/eliminar.html')

from django.shortcuts import render, redirect


def verdatosu(request, id):
    usuario = get_object_or_404(Registro, id=id)

    if request.method == 'POST':
        form = RegistroForm(request.POST, instance=usuario)#datos enviados por el usuario y indico que voy a editar para qur no me guarde un nuevo usuario si no que se edite 
        if form.is_valid():
            form.save()#metodo para poder guardar los cambios en usuarios
            return redirect('usuarios')
    else:
        form = RegistroForm(instance=usuario)

    return render(request, 'verdatosu/verdatosu.html', {#Se crea el formulario con los datos del usuario para que aparezcan llenos y se puedan editar
        'form': form,#Se envían esos datos al HTML para mostrarlos en la página
        'usuario': usuario
    })


def gestion(request):
    return render(request, 'gestion/gestion.html')


def usuarios(request):
    lista_registros = Registro.objects.filter(tipo_usuario="residente").order_by('-id')

    paginator = Paginator(lista_registros, 5)
    page_number = request.GET.get('page')
    registros = paginator.get_page(page_number)

    return render(request, 'usuarios/usuarios.html', {
        'registros': registros
    })

def ajustes(request):
    return render(request, 'ajustes/ajustes.html')

def editarh(request):
    return render(request, 'editarh/editarh.html')





def generar_numero_tarjeta():
    ultimo = Tarjeta.objects.aggregate(Max("numero"))["numero__max"]
    return str(int(ultimo) + 1) if ultimo else "1000"


def tarjetas(request):
    query = request.GET.get("buscar", "")

    registros_list = Registro.objects.select_related(
        "tarjeta"
    ).prefetch_related(
        "tarjeta__puertas"
    ).all().order_by("-id")

    if query:
        registros_list = registros_list.filter(
            Q(nombre__icontains=query) |  # filtramos por nombre del usuario
            Q(documento__icontains=query)  # filtramos por documento del usuario
        )

    paginator = Paginator(registros_list, 5)
    page_number = request.GET.get("page")
    registros = paginator.get_page(page_number)

    if request.method == "POST":

        accion = request.POST.get("accion")
        tarjeta_id = request.POST.get("tarjeta_id")

        if accion == "cambiar_estado" and tarjeta_id:

            tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)

            registro = Registro.objects.filter(
                tarjeta=tarjeta
            ).first()  # obtenemos el usuario asociado a esa tarjeta

            if registro:
                HistorialTarjeta.objects.create(
                    registro=registro,
                    tarjeta=tarjeta,
                    accion="desactivada" if tarjeta.activa else "activada"
                )  # guardamos el historial del cambio de estado

            tarjeta.activa = not tarjeta.activa  # cambiamos estado activo/inactivo
            tarjeta.save()

        elif accion == "editar_numero" and tarjeta_id:

            tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)
            nuevo_numero = request.POST.get("nuevo_numero")

            if nuevo_numero and not Tarjeta.objects.filter(
                numero=nuevo_numero
            ).exclude(id=tarjeta.id).exists():

                tarjeta.numero = nuevo_numero
                tarjeta.save()

                messages.success(
                    request,
                    "Tarjeta editada correctamente"
                )  # mensaje de éxito al editar

            else:
                messages.error(
                    request,
                    "La tarjeta ya ha sido asignada"
                )  # mensaje si el número ya existe

        elif accion == "cambiar_tarjeta" and tarjeta_id:

            tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)

            registro = get_object_or_404(
                Registro,
                tarjeta=tarjeta
            )

            HistorialTarjeta.objects.create(
                registro=registro,
                tarjeta=tarjeta,
                accion="desactivada"
            )  # registro de cambio de tarjeta

            tarjeta.activa = False  # desactivamos la tarjeta anterior
            tarjeta.save()

            nueva_tarjeta = Tarjeta.objects.create(
                numero=generar_numero_tarjeta(),
                activa=True
            )  # creamos nueva tarjeta

            puertas_ids = request.POST.getlist("puertas")

            if puertas_ids:
                nueva_tarjeta.puertas.set(puertas_ids)  # asignamos puertas a la nueva tarjeta

            registro.tarjeta = nueva_tarjeta  # asignamos la nueva tarjeta al usuario
            registro.save()

            HistorialTarjeta.objects.create(
                registro=registro,
                tarjeta=nueva_tarjeta,
                accion="cambiada"
            )  # historial de cambio de tarjeta

        return redirect("tarjetas")

    puertas = Puerta.objects.all()

    return render(request, "tarjetas/tarjetas.html", {
        "registros": registros,
        "query": query,
        "puertas": puertas
    })


def asignartarjeta(request):
    query = request.GET.get("buscar", "")

    registros_list = Registro.objects.all().order_by("-id")

    if query:
        registros_list = registros_list.filter(
            Q(nombre__icontains=query) |
            Q(documento__icontains=query)
        )

    paginator = Paginator(registros_list, 5)
    page_number = request.GET.get("page")
    registros = paginator.get_page(page_number)

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
        "puertas": puertas
    })

def historialtarjeta(request):
    historial_list = HistorialTarjeta.objects.select_related(
        "registro", "tarjeta"
    ).order_by("-fecha")

    paginator = Paginator(historial_list, 10)
    page_number = request.GET.get("page")
    historial = paginator.get_page(page_number)

    return render(request, "historialtarjeta/historialtarjeta.html", {
        "historial": historial
    })

def estado_legible(self):
    if self.accion == "activada":
        return "Tarjeta activa"
    elif self.accion == "desactivada":
        return "Tarjeta desactivada"
    return self.accion

def control(request):
    datos = Dispositivo.objects.select_related("puerta").all()
    return render(request, "control/control.html", {"datos": datos})

def editart(request):
    return render(request, 'editart/editart.html')

def buscar(request):
    return render(request, 'buscar/buscar.html')

def editaracc(request):
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
    puertas = Puerta.objects.all()
    return render(request, 'puertas/puertas.html', {"puertas": puertas})

def paquetes(request):
    lista_paquetes = Paquetes.objects.all().order_by('-id')

    paginator = Paginator(lista_paquetes, 5)
    page_number = request.GET.get('page')
    paquetes = paginator.get_page(page_number)

    return render(request, 'paquetes/paquetes.html', {
        'paquetes': paquetes
    })
    

def visitantes(request):
    lista_registros = Registro.objects.filter(tipo_usuario="visitante").order_by('-id')

    paginator = Paginator(lista_registros, 5)
    page_number = request.GET.get('page')
    registros = paginator.get_page(page_number)

    return render(request, 'visitantes/visitantes.html', {
        'registros': registros
    })


def editarvisi(request, id):
    usuario = get_object_or_404(Registro, id=id)

    if request.method == 'POST':
        form = RegistroForm(request.POST, instance=usuario)#datos enviados por el usuario y indico que voy a editar para qur no me guarde un nuevo usuario si no que se edite 
        if form.is_valid():
            form.save()#metodo para poder guardar los cambios en usuarios
            return redirect('visitantes')
    else:
        form = RegistroForm(instance=usuario)

    return render(request, 'editarvisi/editarvisi.html', {#Se crea el formulario con los datos del usuario para que aparezcan llenos y se puedan editar
        'form': form,#Se envían esos datos al HTML para mostrarlos en la página
        'usuario': usuario
    })


def editarpa(request, id):
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

    return render(request, 'ip/ip.html')



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

    persona = request.GET.get("persona", "")
    torre = request.GET.get("torre", "")
    fecha = request.GET.get("fecha", "")
    puerta = request.GET.get("puerta", "")

    # evitar errores cuando llegue "None"
    if persona == "None":
        persona = ""

    if torre == "None":
        torre = ""

    if fecha == "None":
        fecha = ""

    if puerta == "None":
        puerta = ""

    lista = RegistroAcceso.objects.select_related(
        "persona"
    ).order_by(
        "-fecha",
        "-hora_entrada"
    )

    # filtro persona
    if persona:
        lista = lista.filter(
            Q(persona__nombre__icontains=persona) |
            Q(persona__documento__icontains=persona)
        )

    # filtro torre
    if torre:

        torre = torre.lower().replace(" ", "")

        if "torre" in torre:
            numero = "".join(filter(str.isdigit, torre))
            if numero:
                torre = f"torre_{numero}"

        lista = lista.filter(
            torre__icontains=torre
        )

    # filtro fecha
    if fecha:
        lista = lista.filter(
            fecha=fecha
        )


    if puerta:

        puerta_limpia = limpiar_texto(puerta)

        lista = lista.filter(
            Q(puerta__icontains=puerta_limpia) |
            Q(tipo_acceso__icontains=puerta_limpia)
        )

    paginator = Paginator(lista, 6)

    page_number = request.GET.get("page")

    registros = paginator.get_page(page_number)

    return render(
        request,
        "historialacceso/historialacceso.html",
        {
            "registros": registros,
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

    def limpiar(v):
        if v in [None, "", "None"]:
            return None
        return v

    persona = limpiar(persona)
    torre = limpiar(torre)
    fecha = limpiar(fecha)
    puerta = limpiar(puerta)

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
            from_email="tucorreo@gmail.com",
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