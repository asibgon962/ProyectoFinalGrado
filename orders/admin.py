from django.contrib import admin
from .models import SolicitudServicio
import json

@admin.register(SolicitudServicio)
class SolicitudServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre_entidad', 'tipo_servicio', 'fecha_entrega', 'mostrar_cantidades', 'estado')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('nombre_entidad', 'usuario__username')
    
    # Excluimos este campo para que no moleste en el admin, los datos reales van en el JSON
    exclude = ('productos_solicitados',)
    
    def mostrar_cantidades(self, obj):
        detalles = obj.detalles_cantidades
        if isinstance(detalles, str):
            try:
                detalles = json.loads(detalles)
            except:
                return "Error de formato"

        if detalles and isinstance(detalles, dict):
            # Como ahora guardaremos el NOMBRE en el JSON desde el frontend, lo mostramos directo
            resumen = [f"{nombre_plato} (x{cantidad})" for nombre_plato, cantidad in detalles.items()]
            return ", ".join(resumen) or "Sin productos"
            
        return "N/A"
    
    mostrar_cantidades.short_description = "Productos y Cantidades"