from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import SolicitudServicio, MensajeSolicitud
import json

class MensajeSolicitudInline(admin.TabularInline):
    model = MensajeSolicitud
    extra = 1
    exclude = ('es_admin',)

@admin.register(SolicitudServicio)
class SolicitudServicioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_entidad', 'tipo_servicio', 'fecha_entrega', 'mostrar_cantidades', 'estado', 'boton_chat')
    list_display_links = ('id', 'nombre_entidad')
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
    
    def boton_chat(self, obj):
        url = reverse('admin_chat_detail', args=['solicitud', obj.id])
        return format_html('<a class="button" href="{}" style="background: #d4af37; color: black; font-weight: bold; border-radius: 5px; padding: 4px 8px; text-decoration: none;">💬 Chat</a>', url)
    
    boton_chat.short_description = "Chat en Vivo"



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
    list_display = ('id', 'organizacion', 'fecha_pedido', 'estado', 'total', 'boton_chat')
    list_display_links = ('id', 'organizacion')
    list_editable = ('estado',)
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('organizacion__nombre', 'usuario__username')
    inlines = [ItemPedidoMercadoInline, MensajePedidoMercadoInline]

    def boton_chat(self, obj):
        url = reverse('admin_chat_detail', args=['mercado', obj.id])
        return format_html('<a class="button" href="{}" style="background: #d4af37; color: black; font-weight: bold; border-radius: 5px; padding: 4px 8px; text-decoration: none;">💬 Chat</a>', url)
    
    boton_chat.short_description = "Chat en Vivo"
