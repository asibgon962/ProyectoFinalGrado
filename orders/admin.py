from django.contrib import admin
from .models import SolicitudServicio
from catalog.models import Plato # <--- CAMBIO CLAVE: Importamos de catalog
import json

@admin.register(SolicitudServicio)
class SolicitudServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre_entidad', 'tipo_servicio', 'fecha_entrega', 'mostrar_cantidades', 'estado')
    list_filter = ('estado', 'tipo_servicio', 'fecha_entrega')
    search_fields = ('nombre_entidad', 'usuario__username')
    
    def mostrar_cantidades(self, obj):
        detalles = obj.detalles_cantidades
        
        # Si el dato en DB es un string, lo parseamos
        if isinstance(detalles, str):
            try:
                detalles = json.loads(detalles)
            except:
                return "Error de formato"

        if detalles and isinstance(detalles, dict):
            resumen = []
            for plato_id, cantidad in detalles.items():
                try:
                    # Buscamos el plato en el catálogo
                    plato = Plato.objects.get(id=plato_id)
                    resumen.append(f"{plato.nombre} (x{cantidad})")
                except (Plato.DoesNotExist, ValueError):
                    continue
            return ", ".join(resumen) or "Sin productos"
            
        return "N/A"
    
    mostrar_cantidades.short_description = "Productos y Cantidades"