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