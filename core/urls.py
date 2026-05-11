"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import HttpResponse
from catalog.views import home_view, restaurante_view
from orders.views import solicitar_servicio
from users import views
from users.views import register_view, profile_view, editar_perfil_view
from catalog.views import (
    menu_view, 
    mercado_negro_view, 
    agregar_carrito, 
    ver_carrito, 
    vaciar_carrito, 
    eliminar_item_carrito,
    procesar_compra,
    aplicar_oferta_mercado,
    aplicar_cupon,
    aplicar_oferta_servicio,
    validar_cupon_ajax
)
from orders import views as orders_views
from orders.views import accion_estado

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('robots.txt', lambda r: HttpResponse(
        "User-agent: *\nDisallow: /admin/\nDisallow: /accounts/\nDisallow: /mercado-negro/\nDisallow: /organizacion/\nDisallow: /mis-gestiones/\nDisallow: /editar-perfil/\nDisallow: /profile/\nDisallow: /solicitar/\nAllow: /",
        content_type="text/plain"
    )),
    path('', home_view, name='home'),
    path('restaurante/', restaurante_view, name='restaurante'),
    path('profile/', profile_view, name='profile'),
    path('solicitar/', solicitar_servicio, name='solicitar_servicio'),
    path('register/', register_view, name='register'),
    path('editar-perfil/', editar_perfil_view, name='editar_perfil'),
    path('privacidad/', views.privacidad, name='privacidad'),
    path('terminos/', views.terminos, name='terminos'),
    path('contacto/', views.contacto, name='contacto'),
    path('servicios/', views.servicios, name='servicios'),
    path('menu/', menu_view, name='menu'),
    path('organizacion/', orders_views.panel_organizacion, name='mi_organizacion'),
    path('organizacion/<int:solicitud_id>/', orders_views.panel_organizacion, name='mi_organizacion_chat'),
    path('mis-gestiones/', orders_views.mis_gestiones, name='mis_gestiones'),
    path('mis-gestiones/<int:solicitud_id>/', orders_views.mis_gestiones, name='mis_gestiones_chat'),
    path('organizacion/mercado/<int:pedido_id>/', orders_views.panel_organizacion_mercado, name='mi_mercado_chat'),
    path('enviar-mensaje/<int:solicitud_id>/', orders_views.enviar_mensaje, name='enviar_mensaje'),
    path('enviar-mensaje-mercado/<int:pedido_id>/', orders_views.enviar_mensaje_mercado, name='enviar_mensaje_mercado'),
    path('mercado-negro/', mercado_negro_view, name='mercado_negro'),
    path('mercado-negro/agregar/<int:producto_id>/', agregar_carrito, name='agregar_carrito'),
    path('mercado-negro/eliminar/<int:producto_id>/', eliminar_item_carrito, name='eliminar_item_carrito'),
    path('mercado-negro/carrito/', ver_carrito, name='ver_carrito'),
    path('mercado-negro/vaciar-carrito/', vaciar_carrito, name='vaciar_carrito'),
    path('mercado-negro/procesar/', procesar_compra, name='procesar_compra'),
    path('mercado-negro/oferta/<int:oferta_id>/', aplicar_oferta_mercado, name='aplicar_oferta_mercado'),
    path('mercado-negro/cupon/', aplicar_cupon, name='aplicar_cupon'),
    path('validar-cupon-ajax/', validar_cupon_ajax, name='validar_cupon_ajax'),
    path('servicio/oferta/<int:oferta_id>/', aplicar_oferta_servicio, name='aplicar_oferta_servicio'),
    path('admin-chat/', orders_views.admin_chat_dashboard, name='admin_chat_dashboard'),
    path('admin-chat/<str:chat_type>/<int:object_id>/', orders_views.admin_chat_dashboard, name='admin_chat_detail'),
    path('orders/accion/<str:tipo>/<int:objeto_id>/<str:nuevo_estado>/', accion_estado, name='accion_estado'),
    path('ping/', lambda r: HttpResponse("pong", content_type="text/plain"), name='ping'),
]

if settings.DEBUG:
    # Sirve archivos subidos por usuarios (Avatares en /media/)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Sirve archivos estáticos (CSS, JS, imágenes de diseño en /static/)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


