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
from catalog.views import home_view
from orders.views import solicitar_servicio
from users import views
from users.views import register_view, profile_view, editar_perfil_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home_view, name='home'),
    path('profile/', profile_view, name='profile'),
    path('solicitar/', solicitar_servicio, name='solicitar_servicio'),
    path('register/', register_view, name='register'),
    path('editar-perfil/', editar_perfil_view, name='editar_perfil'),
    path('privacidad/', views.privacidad, name='privacidad'),
    path('terminos/', views.terminos, name='terminos'),
    path('contacto/', views.contacto, name='contacto'),
]

if settings.DEBUG:
    # Sirve archivos subidos por usuarios (Avatares en /media/)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Sirve archivos estáticos (CSS, JS, imágenes de diseño en /static/)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


