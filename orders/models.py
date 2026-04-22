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
    
    # Datos en formato JSON para flexibilidad
    detalles_cantidades = models.JSONField(default=dict, blank=True)
    detalles_transporte = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.nombre_entidad} - {self.fecha_entrega}"

class MensajeSolicitud(models.Model):
    solicitud = models.ForeignKey(SolicitudServicio, on_delete=models.CASCADE, related_name='mensajes')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    es_admin = models.BooleanField(default=False)

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

    class Meta:
        ordering = ['fecha_envio']

    def __str__(self):
        return f"Mensaje en MN {self.pedido.id} por {self.usuario.username}"

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