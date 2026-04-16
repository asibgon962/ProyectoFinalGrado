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
from django.urls import path, include  # ¡Asegúrate de tener el include!
from django.views.generic import TemplateView
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
    procesar_compra
)
from orders import views as orders_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('robots.txt', TemplateView.as_view(template_name='../static/robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='../static/sitemap.xml', content_type='application/xml')),
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
]

if settings.DEBUG:
    # Sirve archivos subidos por usuarios (Avatares en /media/)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Sirve archivos estáticos (CSS, JS, imágenes de diseño en /static/)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


