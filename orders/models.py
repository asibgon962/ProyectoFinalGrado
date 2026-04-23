from django.db import models
from django.conf import settings
from catalog.models import Plato
from multiselectfield import MultiSelectField
from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class SolicitudServicio(models.Model):
    TIPO_CHOICES = [
        ('EVENTO', 'Catering para Evento'),
        ('SUMINISTRO', 'Suministro a Restaurante'),
        ('TRANSPORTE', 'Logística y Transporte VIP'),
    ]

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('ACEPTADO', 'Presupuestado / Aceptado'),
        ('EN_CAMINO', 'En Reparto'),
        ('COMPLETADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes')
    organizacion = models.ForeignKey('users.Organization', on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_empresa')
    
    tipo_servicio = MultiSelectField(choices=TIPO_CHOICES, max_length=150, verbose_name="Tipos de Servicio")
    nombre_entidad = models.CharField(max_length=200)
    fecha_entrega = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    observaciones = models.TextField(blank=True, null=True)
    
    # Campos booleanos para lógica de negocio
    requiere_productos = models.BooleanField(default=False)
    requiere_transporte = models.BooleanField(default=False)
    
    detalles_cantidades = models.JSONField(default=dict, blank=True)
    detalles_transporte = models.JSONField(default=dict, blank=True)

    oferta_aplicada = models.ForeignKey(
        'catalog.OfertaServicio', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='solicitudes'
    )
    precio_fijo = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Si viene de una oferta, este será el precio final acordado."
    )

    def __str__(self):
        return f"{self.nombre_entidad} - {self.fecha_entrega}"

class MensajeSolicitud(models.Model):
    solicitud = models.ForeignKey(SolicitudServicio, on_delete=models.CASCADE, related_name='mensajes')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    es_admin = models.BooleanField(default=False)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['fecha_envio']

from catalog.models import Producto

class PedidoMercado(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Pago/Revisión'),
        ('ACEPTADO', 'En Proceso'),
        ('EN_CAMINO', 'En Reparto'),
        ('COMPLETADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos_mercado')
    organizacion = models.ForeignKey('users.Organization', on_delete=models.CASCADE, related_name='pedidos_mercado_empresa')
    
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    stock_descontado = models.BooleanField(default=False)

    oferta_aplicada = models.ForeignKey(
        'catalog.OfertaMercado', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='pedidos'
    )
    cupon_aplicado = models.ForeignKey(
        'catalog.Cupon', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='pedidos'
    )
    descuento_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def clean(self):
        super().clean()
        if self.estado in ['EN_CAMINO', 'COMPLETADO'] and getattr(self, 'stock_descontado', False) == False:
            errores = []
            if self.pk: # Solo validar si el pedido existe y tiene items
                for item in self.items.all():
                    if item.producto and item.producto.stock < item.cantidad:
                        errores.append(f"Stock insuficiente para '{item.producto.nombre}'. Pides: {item.cantidad}, Cuentas con: {item.producto.stock}")
            
            if errores:
                from django.core.exceptions import ValidationError
                raise ValidationError({"estado": " | ".join(errores)})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.estado in ['EN_CAMINO', 'COMPLETADO'] and not self.stock_descontado:
            for item in self.items.all():
                if item.producto:
                    item.producto.stock -= item.cantidad
                    item.producto.save()
            self.stock_descontado = True
            super().save(update_fields=['stock_descontado'])

    def __str__(self):
        return f"Pedido MN #{self.id} - {self.organizacion.nombre}"

class ItemPedidoMercado(models.Model):
    pedido = models.ForeignKey(PedidoMercado, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        if self.cantidad is None or self.precio_unitario is None:
            return 0
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre if self.producto else 'Desconocido'}"

class MensajePedidoMercado(models.Model):
    pedido = models.ForeignKey(PedidoMercado, on_delete=models.CASCADE, related_name='mensajes')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    es_admin = models.BooleanField(default=False)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['fecha_envio']

    def __str__(self):
        return f"Mensaje en MN {self.pedido.id} por {self.usuario.username}"

# --- SEÑALES PARA DISCORD ---

@receiver(post_save, sender=SolicitudServicio)
def notificar_nueva_solicitud(sender, instance, created, **kwargs):
    if created:
        from .utils import send_discord_notification, generar_links_accion
        title = f"🚨 Nueva Solicitud de Servicio #{instance.id}"

        # Formatear tipos de servicio (MultiSelectField)
        tipos = ", ".join([dict(SolicitudServicio.TIPO_CHOICES).get(t, t) for t in instance.tipo_servicio])

        # --- Platos solicitados (detalles_cantidades = {"Nombre": cantidad}) ---
        platos_str = ""
        if instance.detalles_cantidades:
            lineas = [f"• {nombre}: {cant} uds." for nombre, cant in instance.detalles_cantidades.items()]
            platos_str = "\n".join(lineas)

        # --- Transporte VIP (detalles_transporte = {"Tipo": cantidad}) ---
        transporte_str = ""
        if instance.detalles_transporte:
            lineas_t = [f"• {tipo}: {cant}" for tipo, cant in instance.detalles_transporte.items()]
            transporte_str = "\n".join(lineas_t)

        # Construir descripción enriquecida
        description = f"**{instance.usuario.username}** ha creado una nueva solicitud de servicio."
        if platos_str:
            description += f"\n\n**🍽️ Platos solicitados:**\n{platos_str}"
        if transporte_str:
            description += f"\n\n**🚗 Transporte VIP:**\n{transporte_str}"

        fields = [
            {"name": "Entidad / Evento", "value": instance.nombre_entidad, "inline": True},
            {"name": "Tipo de Servicio", "value": tipos, "inline": True},
            {"name": "Fecha Entrega", "value": str(instance.fecha_entrega), "inline": True},
        ]

        if instance.organizacion:
            fields.append({"name": "Organización", "value": instance.organizacion.nombre, "inline": True})

        # ── Links de acción firmados ──────────────────────────────────────────
        links = generar_links_accion('solicitud', instance.id)
        links_texto = "  ·  ".join(f"[{l['label']}]({l['url']})" for l in links)
        fields.append({"name": "⚡ Cambiar estado", "value": links_texto, "inline": False})
        # ─────────────────────────────────────────────────────────────────────

        admin_url = f"https://koienterprise.onrender.com/admin/orders/solicitudservicio/{instance.id}/change/"

        send_discord_notification('servicios', title, description, fields, url=admin_url)

@receiver(post_save, sender=PedidoMercado)
def notificar_nuevo_pedido_mn(sender, instance, created, **kwargs):
    pass  # Notificación movida a catalog/views.py::procesar_compra para que incluya total e items correctos

# --- SEÑALES PARA WEBSOCKETS ---

@receiver(post_save, sender=MensajeSolicitud)
def broadcast_mensaje_solicitud(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_solicitud_{instance.solicitud.id}',
            {
                'type': 'chat_message',
                'message': instance.texto,
                'username': instance.usuario.username,
                'es_admin': instance.es_admin,
                'fecha_envio': instance.fecha_envio.strftime('%H:%M')
            }
        )

@receiver(post_save, sender=MensajePedidoMercado)
def broadcast_mensaje_mercado(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_mercado_{instance.pedido.id}',
            {
                'type': 'chat_message',
                'message': instance.texto,
                'username': instance.usuario.username,
                'es_admin': instance.es_admin,
                'fecha_envio': instance.fecha_envio.strftime('%H:%M')
            }
        )