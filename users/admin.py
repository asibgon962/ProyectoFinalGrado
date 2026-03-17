from django.contrib import admin
from .models import User, Organization

admin.site.register(User)
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_grupo', 'es_ilegal')