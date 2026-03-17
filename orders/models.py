from django.db import models
from django.conf import settings
from catalog.models import Plato

class SolicitudServicio(models.Model):
    TIPO_CHOICES = [
        ('EVENTO', 'Catering para Evento'),
        ('SUMINISTRO', 'Suministro a Restaurante'),
        ('TRANSPORTE', 'Logística y Transporte VIP'),
    ]

    # --- NUEVOS CHOICES PARA VEHÍCULOS ---
    VEHICULO_CHOICES = [
        ('LIMUSINA', 'Limusina (2 disponibles/día)'),
        ('JET', 'Jet Privado (2 disponibles/día)'),
        ('CAMION', 'Camión de Carga (2 disponibles/día)'),
    ]

    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('ACEPTADO', 'Presupuestado / Aceptado'),
        ('EN_CAMINO', 'En Reparto'),
        ('COMPLETADO', 'Finalizado'),
        ('CANCELADO', 'Cancelado'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    tipo_servicio = models.CharField(max_length=20, choices=TIPO_CHOICES, default='EVENTO')
    nombre_entidad = models.CharField(max_length=200)
    fecha_entrega = models.DateField()
    observaciones = models.TextField(blank=True, null=True)
    
    # PRODUCTOS
    requiere_productos = models.BooleanField(default=False) # Cambiado a False por defecto
    productos_solicitados = models.ManyToManyField(Plato, blank=True)
    
    # --- NUEVO CAMPO PARA CANTIDADES ---
    # Guardará algo como: {"1": 5, "4": 2} (ID del plato: Cantidad)
    detalles_cantidades = models.JSONField(default=dict, blank=True, null=True)

    # TRANSPORTE
    requiere_transporte = models.BooleanField(default=False)
    # --- NUEVO CAMPO PARA VEHÍCULO ESPECÍFICO ---
    detalles_transporte = models.JSONField(default=dict, blank=True, null=True, help_text="Guarda los vehículos seleccionados y sus cantidades: {'Limusina': 2, 'Jet': 1}")
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    creado_el = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_entidad} - {self.get_tipo_servicio_display()}"