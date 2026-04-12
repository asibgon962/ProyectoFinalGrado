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

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='solicitudes'
    )
    
    # SOLUCIÓN CON LIBRERÍA DE TERCEROS
    tipo_servicio = MultiSelectField(
        choices=TIPO_CHOICES,
        max_length=150,
        verbose_name="Tipos de Servicio"
    )
    
    nombre_entidad = models.CharField(max_length=200)
    fecha_entrega = models.DateField()
    observaciones = models.TextField(blank=True, null=True)
    
    requiere_productos = models.BooleanField(default=False)
    productos_solicitados = models.ManyToManyField(Plato, blank=True)
    
    detalles_cantidades = models.JSONField(default=dict, blank=True)
    
    requiere_transporte = models.BooleanField(default=False)
    detalles_transporte = models.JSONField(default=dict, blank=True)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    creado_el = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_entidad} - {self.estado}"