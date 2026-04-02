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