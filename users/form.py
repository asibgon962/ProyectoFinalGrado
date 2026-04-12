import re
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Profile, Organization


User = get_user_model()

class RegistroUsuarioForm(forms.ModelForm):
    # ID CODE: # + 4 letras (Total 5 caracteres)
    id_code = forms.CharField(
        max_length=5, 
        min_length=5,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'ID (Ej: #ABCD)'}),
        error_messages={
            'required': 'El ID es obligatorio.',
            'min_length': 'El ID debe tener exactamente 5 caracteres (Ej: #ABCD).',
            'max_length': 'El ID no puede exceder los 5 caracteres.'
        }
    )

    # TELÉFONO: Exactamente 6 números
    telefono = forms.CharField(
        max_length=6, 
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Teléfono (6 dígitos)'}),
        error_messages={
            'required': 'El teléfono es obligatorio.',
            'min_length': 'El teléfono debe tener exactamente 6 dígitos.',
            'max_length': 'El teléfono no puede exceder los 6 dígitos.'
        }
    )

    # CÓDIGO EMPRESA: Opcional
    codigo_empresa = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Código de Organización (Opcional)'})
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
        required=True,
        error_messages={'required': 'La contraseña es obligatoria.'}
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar Contraseña'}),
        required=True,
        error_messages={'required': 'Debes confirmar la contraseña.'}
    )

    class Meta:
        model = User
        fields = ['username', 'id_code', 'telefono', 'codigo_empresa', 'password1', 'password2']
        error_messages = {
            'username': {
                'required': 'El nombre de ciudadano es obligatorio.',
                'unique': 'Este nombre ya está registrado en el sistema.',
            }
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and not re.match(r'^[a-zA-Z]+_[a-zA-Z]+$', username):
            raise ValidationError("El formato debe ser Nombre_Apellido (Ej: Juan_Perez).")
        return username

    def clean_id_code(self):
        id_code = self.cleaned_data.get('id_code')
        if id_code and not re.match(r'^#[A-Z]{4}$', id_code):
            raise ValidationError("El ID debe empezar por # seguido de 4 letras MAYÚSCULAS.")
        return id_code

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.isdigit():
            raise ValidationError("El teléfono solo puede contener números.")
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.id_code = self.cleaned_data.get('id_code')
        user.telefono = self.cleaned_data.get('telefono')
        user.codigo_empresa = self.cleaned_data.get('codigo_empresa')
        if commit:
            user.save()
        return user


class EditarPerfilForm(forms.ModelForm):
    # Campo para editar el código de organización (vinculado al User)
    codigo_grupo = forms.CharField(
        max_length=50, 
        required=False, 
        label="Código de Organización/Empresa",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Introduce el código...'})
    )

    # Opciones de avatar predeterminado
    AVATAR_PREDETERMINADO_CHOICES = [
        ('none', 'Mantener actual / Subir personalizado'),
        ('masculino', 'Perfil Masculino'),
        ('femenino', 'Perfil Femenino'),
    ]
    
    avatar_option = forms.ChoiceField(
        choices=AVATAR_PREDETERMINADO_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'btn-check'}), # Clase para Bootstrap
        initial='none',
        required=False,
    )

    class Meta:
        model = Profile
        fields = ['avatar', 'telefono', 'biografia']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'id': 'file_input'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'biografia': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.isdigit():
            raise ValidationError("El teléfono solo puede contener números.")
        if telefono and len(telefono) != 6:
            raise ValidationError("El teléfono debe tener exactamente 6 dígitos.")
        return telefono