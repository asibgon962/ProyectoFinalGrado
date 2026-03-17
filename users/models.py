from django.db import models
from django.contrib.auth.models import AbstractUser

class Organization(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_grupo = models.CharField(max_length=20, unique=True)
    es_ilegal = models.BooleanField(default=False) # Para acceso a Dark Web

    def __str__(self):
        return self.nombre

class User(AbstractUser):
    # Relación con la organización (Many-to-One)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='members'
    )

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ['orden']

    def __str__(self):
        return self.nombre

class Plato(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='platos')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='platos/')
    es_destacado = models.BooleanField(default=False, help_text="Aparecerá en el carrusel de inicio")
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class SolicitudServicio(models.Model):
    TIPOS_SERVICIO = [
        ('EVENTO', 'Catering y Logística para Eventos'),
        ('SUMINISTRO', 'Abastecimiento a Restaurantes Externos'),
        ('TRANSPORTE', 'Solo Transporte VIP/Artistas'),
    ]
    
    usuario = models.ForeignKey('User', on_delete=models.CASCADE, related_name='solicitudes')
    tipo_servicio = models.CharField(max_length=20, choices=TIPOS_SERVICIO)
    
    # --- Datos del Cliente/Destino ---
    nombre_entidad = models.CharField(max_length=200, help_text="Nombre del Festival o Restaurante cliente")
    fecha_entrega = models.DateTimeField(verbose_name="Fecha del servicio o suministro")

    # --- Detalle del Pedido (Comida/Productos) ---
    requiere_productos = models.BooleanField(default=False, verbose_name="¿Incluye alimentos/suministros?")
    productos_solicitados = models.ManyToManyField('Plato', blank=True, verbose_name="Productos/Platos a suministrar")
    
    # --- Detalle de Logística ---
    requiere_transporte = models.BooleanField(default=False, verbose_name="¿Requiere flota de transporte Koi?")
    volumen_logistica = models.TextField(blank=True, help_text="Descripción del transporte (ej: 3 furgones refrigerados, 2 sedanes VIP)")

    estado = models.CharField(max_length=20, choices=[
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('PROCESO', 'En Preparación/Tránsito'),
        ('COMPLETADO', 'Entregado'),
    ], default='PENDIENTE')

    def __str__(self):
        return f"{self.get_tipo_servicio_display()} - {self.nombre_entidad}"
    

    