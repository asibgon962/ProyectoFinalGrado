from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Información de Perfil'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    # Columnas que verás en la lista de usuarios
    list_display = ('username', 'id_code', 'get_telefono', 'organization', 'is_staff')
    list_filter = ('organization', 'is_staff', 'is_superuser')
    
    # Añadimos los campos personalizados al editor del admin
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Ciudadano', {'fields': ('id_code', 'organization')}),
    )

    def get_telefono(self, obj):
        return obj.profile.telefono
    get_telefono.short_description = 'Teléfono'

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_grupo', 'es_ilegal')
    search_fields = ('nombre', 'codigo_grupo')
    list_filter = ('es_ilegal',)

from django.core.mail import send_mail
from .models import MensajeContacto
import uuid

@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ('asunto', 'nombre', 'email', 'fecha_envio', 'contestado')
    list_filter = ('contestado', 'fecha_envio')
    search_fields = ('nombre', 'email', 'asunto')
    readonly_fields = ('nombre', 'email', 'asunto', 'mensaje', 'fecha_envio', 'contestado')

    def get_form(self, request, obj=None, **kwargs):
        if obj and not obj.respuesta and obj.asunto == "Crear empresa":
            codigo = str(uuid.uuid4())[:8].upper()
            obj.respuesta = f"Hola {obj.nombre},\n\nAtendiendo a tu solicitud, aquí tienes el código de tu nueva empresa para registrarte o vincularte:\nCódigo: {codigo}\n\nGracias por confiar en Koi Enterprise."
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if obj.respuesta and not obj.contestado:
            send_mail(
                subject=f"RE: {obj.asunto} - Koi Enterprise",
                message=obj.respuesta,
                from_email=None,
                recipient_list=[obj.email],
                fail_silently=False,
            )
            obj.contestado = True
            self.message_user(request, "Correo de respuesta enviado en consola y marcado como contestado.")
        
        super().save_model(request, obj, form, change)