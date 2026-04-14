from django.contrib import admin
from .models import SolicitudServicio, MensajeSolicitud
import json

class MensajeSolicitudInline(admin.TabularInline):
    model = MensajeSolicitud
    extra = 1
    exclude = ('es_admin',)

@admin.register(SolicitudServicio)
class SolicitudServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre_entidad', 'tipo_servicio', 'fecha_entrega', 'mostrar_cantidades', 'estado')
    list_editable = ('estado',)
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('nombre_entidad', 'usuario__username')
    exclude = ('productos_solicitados',)
    inlines = [MensajeSolicitudInline]
    
    def mostrar_cantidades(self, obj):
        detalles = obj.detalles_cantidades
        if isinstance(detalles, str):
            try:
                detalles = json.loads(detalles)
            except:
                return "Error de formato"

        if detalles and isinstance(detalles, dict):
            resumen = [f"{nombre_plato} (x{cantidad})" for nombre_plato, cantidad in detalles.items()]
            return ", ".join(resumen) or "Sin productos"
            
        return "N/A"
    
    mostrar_cantidades.short_description = "Productos y Cantidades"



from .models import PedidoMercado, ItemPedidoMercado, MensajePedidoMercado

class ItemPedidoMercadoInline(admin.TabularInline):
    model = ItemPedidoMercado
    readonly_fields = ('subtotal',)
    extra = 0

class MensajePedidoMercadoInline(admin.TabularInline):
    model = MensajePedidoMercado
    extra = 1
    exclude = ('es_admin',)

@admin.register(PedidoMercado)
class PedidoMercadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'organizacion', 'fecha_pedido', 'estado', 'total')
    list_editable = ('estado',)
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('organizacion__nombre', 'usuario__username')
    inlines = [ItemPedidoMercadoInline, MensajePedidoMercadoInline]
