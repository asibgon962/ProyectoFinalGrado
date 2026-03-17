from django.contrib import admin
from users.models import Plato
from .models import SolicitudServicio

@admin.register(SolicitudServicio)
class SolicitudServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre_entidad', 'tipo_servicio', 'fecha_entrega', 'mostrar_cantidades', 'estado')
    
    def mostrar_cantidades(self, obj):
        if obj.detalles_cantidades:
            # Creamos una lista legible: "Plato A (x2), Plato B (x5)"
            resumen = []
            for plato_id, cantidad in obj.detalles_cantidades.items():
                try:
                    plato = Plato.objects.get(id=plato_id)
                    resumen.append(f"{plato.nombre} (x{cantidad})")
                except Plato.DoesNotExist:
                    continue
            return ", ".join(resumen)
        return "N/A"
    
    mostrar_cantidades.short_description = "Productos y Cantidades"