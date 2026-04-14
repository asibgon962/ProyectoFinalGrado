from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class Organization(models.Model):
    nombre = models.CharField(max_length=100)
    codigo_grupo = models.CharField(max_length=20, unique=True)
    es_ilegal = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

class User(AbstractUser):
    # Nuevo campo para el ID de ciudadano #XXXX
    id_code = models.CharField(max_length=5, unique=True, null=True, blank=True)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='members'
    )

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    biografia = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/masculino.jpg', blank=True)
    direccion_contacto = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=150)
    email = models.EmailField()
    asunto = models.CharField(max_length=150)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    contestado = models.BooleanField(default=False)
    respuesta = models.TextField(blank=True, null=True, help_text="Escribe la respuesta aquí. Al guardar se enviará este texto por correo al usuario.")

    def __str__(self):
        return f"{self.asunto} - {self.email}"