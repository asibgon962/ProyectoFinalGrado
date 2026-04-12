from django.db import models
from django.conf import settings
from catalog.models import Plato
from multiselectfield import MultiSelectField

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