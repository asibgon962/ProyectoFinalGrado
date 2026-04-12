from django.contrib import admin
from .models import SolicitudServicio
from catalog.models import Plato
import json

@admin.register(SolicitudServicio)
class SolicitudServicioAdmin(admin.ModelAdmin):
    # Usamos mostrar_servicios en lugar del campo directo
    list_display = ('nombre_entidad', 'mostrar_servicios', 'fecha_entrega', 'mostrar_cantidades', 'estado')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('nombre_entidad', 'usuario__username')
    
    def mostrar_servicios(self, obj):
        return obj.get_servicios_display()
    mostrar_servicios.short_description = "Servicios"

    def mostrar_cantidades(self, obj):
        detalles = obj.detalles_cantidades
        if isinstance(detalles, str):
            try: detalles = json.loads(detalles)
            except: return "Error"

        if detalles and isinstance(detalles, dict):
            resumen = []
            for p_id, cant in detalles.items():
                try:
                    plato = Plato.objects.get(id=p_id)
                    resumen.append(f"{plato.nombre} (x{cant})")
                except: continue
            return ", ".join(resumen) or "Sin productos"
        return "N/A"
    
    mostrar_cantidades.short_description = "Productos"