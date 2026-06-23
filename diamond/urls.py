from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import AtencionClienteViewSet
from .views import registrar_acceso
router = DefaultRouter()
router.register(r'atencion', AtencionClienteViewSet)
from .views import cambiar_foto





urlpatterns = [
    path('api/acceso/', registrar_acceso, name='api_acceso'),
    path('cambiar-foto/', cambiar_foto, name='cambiar_foto'),
    path(
    "crear_usuario/",
    views.crear_usuario,
    name="crear_usuario"
),
    
    path('', views.principal, name='principal'),
    path('acceso/', views.acceso, name='acceso'),
    path('contacto/', views.contacto, name='contacto'),
    path('registro/', views.registro, name='registro'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('integraciones/', views.integraciones, name='integraciones'),
    path('recuperar/', views.recuperar, name='recuperar'),
    path("restablecer/<uuid:token>/", views.restablecer, name="restablecer"),
    path('cotizar/', views.cotizar, name='cotizar'),
    path('admin/', views.admin, name='admin'),
    path('horarioad/', views.horarioad, name='horarioad'),
    path('informes/', views.informes, name='informes'),
    path('registroa/', views.registroa, name='registroa'),
    path('ingresousu/', views.ingresousu, name='ingresousu'),
    path('verusuario/', views.verusuario, name='verusuario'),
    path('eliminar/', views.eliminar, name='eliminar'),
    path("verdatosu/<int:id>/", views.verdatosu, name="verdatosu"),
    path('gestion/', views.gestion, name='gestion'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('ajustes/', views.ajustes, name='ajustes'),
    path('editarh/', views.editarh, name='editarh'),
    path('cliente/', views.cliente, name='cliente'),
    path('tarjetas/', views.tarjetas, name='tarjetas'),
    path('control/', views.control, name='control'),
    path('editart/', views.editart, name='editart'),
    path('buscar/', views.buscar, name='buscar'),
    path('editaracc/', views.editaracc, name='editaracc'),
    path('peatones/', views.peatones, name='peatones'),
    path('emergencia/', views.emergencia, name='emergencia'),
    path('discapacitados/', views.discapacitados, name='discapacitados'),
    path('vehiculos/', views.vehiculos, name='vehiculos'),
    path('recepcion/', views.recepcion, name='recepcion'),
    path('puertas/', views.puertas, name='puertas'),
    path('paquetes/', views.paquetes, name='paquetes'),
    path('visitantes/', views.visitantes, name='visitantes'),
    path('editarvisi/<int:id>/', views.editarvisi, name='editarvisi'),
    path('editarpa/<int:id>/', views.editarpa, name='editarpa'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('editarvehi/', views.editarvehi, name='editarvehi'),
    path('ip/', views.ip, name='ip'),
    path('torres/', views.torres, name='torres'),
    path('mensajeria/', views.mensajeria, name='mensajeria'),
    path('historialtarjeta/', views.historialtarjeta, name='historialtarjeta'),
    path('asignartarjeta/', views.asignartarjeta, name='asignartarjeta'),
    path('historialacceso/', views.historialacceso, name='historialacceso'),
    path('apertura/', views.apertura_emergencia, name='apertura_emergencia'),
    path('detener/', views.detener_emergencia, name='detener_emergencia'),
    path('cerrar/', views.cerrar_puertas, name='cerrar_puertas'),
    path('puerta/<int:id>/', views.cambiar_estado_puerta, name='cambiar_puerta'),
    path('reporte-historial-pdf/', views.reporte_historial_pdf, name='reporte_historial_pdf'),
    path('imprimir/', views.imprimir, name='imprimir'),
    path('pdfusuarios/', views.pdfusuarios, name='pdfusuarios'),
    path('pdfpaquetes/', views.pdfpaquetes, name='pdfpaquetes'),
    path('pdfhistorialtarjeta/', views.pdfhistorialtarjeta, name='pdfhistorialtarjeta'),
    path('visitantestem/', views.visitantestem, name='visitantestem'),
    path('registrar_salida/<int:id>/',views.registrar_salida,name='registrar_salida'),
    path('listaingresos',views.listaingresos,name='listaingresos'),
    path('cambiar_foto',views.cambiar_foto,name='cambiar_foto'),
    path('pdfingresos',views.pdfingresos,name='pdfingresos'),
    path('editar_ingreso/<int:id>/', views.editar_ingreso, name='editar_ingreso'),
    path('registrar-entrega/<int:id>/',views.registrar_entrega,name='registrar_entrega'),
    path("detalle-tarjeta/<int:id>/",views.detalle_tarjeta,name="detalle_tarjeta"),
    path("reporte_tarjetas_pdf",views.reporte_tarjetas_pdf,name="reporte_tarjetas_pdf"),
    path("monitoreo/", views.monitoreo, name="monitoreo"),
    path("api/alertas/", views.alertas_api, name="alertas_api"),
    path('logout/', views.cerrar_sesion, name='logout'),
    path("ver_usuarios/",views.ver_usuarios,name="ver_usuarios"),
    path('usuarios/estado/<int:id>/',views.cambiar_estado,name='cambiar_estado'),
    path('usuarios/editar/<int:id>/',views.editar_usuario,name='editar_usuario'),
    path("crear-admin/", views.crear_admin),
 



    
]
urlpatterns += router.urls


