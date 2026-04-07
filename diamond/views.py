from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Solicitud
from .models import Registro
from .models import Cotizacion
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistroForm
from rest_framework import viewsets
from .models import AtencionCliente
from .serializers import AtencionClienteSerializer
from .models import Ip
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Registro, RegistroAcceso
from .serializers import RegistroAccesoSerializer
from .models import Registro, RegistroAcceso
from .serializers import RegistroAccesoSerializer
from .models import Tarjeta
from django.shortcuts import render, redirect
from django.db import IntegrityError
from .models import Registro, Tarjeta
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Max
from django.contrib import messages
from .models import Registro, Tarjeta, HistorialTarjeta
from .models import Registro, Paquetes
from .models import Paquetes
from .forms import PaquetesForm
from .models import Registro
from datetime import date
from .models import Registro

def cliente(request):
    total_usuarios = Registro.objects.count()
    tarjetas_activas = Tarjeta.objects.filter(activa=True).count()
    accesos_hoy = RegistroAcceso.objects.filter(fecha=date.today()).count()

    return render(request, 'cliente/cliente.html', {
        'total_usuarios': total_usuarios,
        'tarjetas_activas': tarjetas_activas,
        'accesos_hoy' : accesos_hoy
        
    })

@api_view(["POST"])#función de vista API
def registrar_acceso(request):#lee los datos
    tarjeta = request.data.get("tarjeta")
    tipo_acceso = request.data.get("tipo_acceso")
    puerta = request.data.get("puerta")
    torre = request.data.get("torre")

    try:#verificar que la tarjeta enviada por la solicitud exista en la tabla
        persona = Registro.objects.get(tarjeta__numero=tarjeta, tarjeta__activa=True)#busca la persona que esta registrada con es número de la tarjeta para despues mostrar sus datos en el registro
        acceso = RegistroAcceso.objects.create(#crea el acceso
            persona=persona,
            tipo_acceso=tipo_acceso,
            puerta=puerta if tipo_acceso == "conjunto" else None,
            torre=torre if tipo_acceso == "torre" else None
        )
        serializer = RegistroAccesoSerializer(acceso)#convierte el objeto acceso a JSON
        return Response(serializer.data, status=201)
    except Registro.DoesNotExist:
        return Response({"error": "Tarjeta no registrada"}, status=404)

class AtencionClienteViewSet(viewsets.ModelViewSet):
    queryset = AtencionCliente.objects.all()
    serializer_class = AtencionClienteSerializer


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

def recuperar(request):
    return render(request, 'recuperar/recuperar.html')

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
                return redirect("residentes")
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
    query = request.GET.get("q", "")

    registros_list = Registro.objects.select_related("tarjeta").all().order_by("-id")

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
        tarjeta_id = request.POST.get("tarjeta_id")
        registro_id = request.POST.get("registro_id")

        if tarjeta_id and accion == "toggle":
            tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)
            tarjeta.activa = not tarjeta.activa
            tarjeta.save()

        elif tarjeta_id and accion == "editar_numero":
            tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)
            nuevo_numero = request.POST.get("nuevo_numero")

            if nuevo_numero and not Tarjeta.objects.filter(
                numero=nuevo_numero
            ).exclude(id=tarjeta.id).exists():
                tarjeta.numero = nuevo_numero
                tarjeta.save()
                messages.success(request, "Tarjeta editada")

        elif accion == "asignar" and registro_id:
            nuevo_numero = request.POST.get("nuevo_numero")

            if nuevo_numero and not Tarjeta.objects.filter(numero=nuevo_numero).exists():
                nueva_tarjeta = Tarjeta.objects.create(
                    numero=nuevo_numero,
                    activa=True
                )

                registro = get_object_or_404(Registro, id=registro_id)
                registro.tarjeta = nueva_tarjeta
                registro.save()

                HistorialTarjeta.objects.create(
                    registro=registro,
                    tarjeta=nueva_tarjeta
                )

                messages.success(request, "Nueva tarjeta asignada")

        elif accion == "cambiar_tarjeta" and tarjeta_id:
            tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id)

            registro = get_object_or_404(Registro, tarjeta=tarjeta)

            tarjeta.activa = False
            tarjeta.save()

            numero = generar_numero_tarjeta()

            nueva_tarjeta = Tarjeta.objects.create(
                numero=numero,
                activa=True
            )

            registro.tarjeta = nueva_tarjeta
            registro.save()

            HistorialTarjeta.objects.create(
                registro=registro,
                tarjeta=nueva_tarjeta
            )

            messages.success(request, "Tarjeta cambiada")

        return redirect("tarjetas")

    return render(request, "tarjetas/tarjetas.html", {
        "registros": registros,
        "query": query
    })




def control(request):
    datos = Ip.objects.all()
    return render(request, "control/control.html", {"datos": datos})

def editart(request):
    return render(request, 'editart/editart.html')

def buscar(request):
    return render(request, 'buscar/buscar.html')

def editaracc(request):
    datos = Ip.objects.all()

    if request.method == "POST":
        registro_id = request.POST.get("id")
        puerta = request.POST.get("puerta")
        ip = request.POST.get("ip")
        estado = "activa" if request.POST.get("estado") else "inactiva"

        registro = Ip.objects.get(id=registro_id)
        registro.puerta = puerta
        registro.ip = ip
        registro.estado = estado
        registro.save()

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
    puertas = Ip.objects.all()
    return render(request, 'puertas/puertas.html',{"puertas":puertas})

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
        puerta = request.POST.get("puerta")
        ip = request.POST.get("ip")
        estado = request.POST.get("estado")
        
        Ip.objects.create(
            puerta = puerta,
            ip = ip,
            estado = estado,    
        )
        return redirect("control")
    
    return render(request, 'ip/ip.html')




