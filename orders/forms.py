from django import forms
from .models import SolicitudServicio
from django.utils import timezone
from datetime import timedelta
import json

class SolicitudServicioForm(forms.ModelForm):
    
    class Meta:
        model = SolicitudServicio
        fields = [
            'tipo_servicio', 
            'nombre_entidad', 
            'fecha_entrega', 
            'requiere_productos', 
            'requiere_transporte', # Añadimos este campo
            'observaciones', 
            'detalles_cantidades',
            'detalles_transporte'
        ]
        
        widgets = {
            'tipo_servicio': forms.SelectMultiple(attrs={
                'class': 'form-select select2', 
                'id': 'id_tipo_servicio'
            }),
            'fecha_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'rows': 3,
                'placeholder': 'Detalles adicionales...'
            }),
            # Ocultamos los cuadros blancos del JSON
            'detalles_cantidades': forms.HiddenInput(),
            'detalles_transporte': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        # Extraemos el usuario que le pasaremos desde la vista
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        self.fields['detalles_cantidades'].initial = "{}"
        self.fields['detalles_transporte'].initial = "{}"

        # --- NUEVO: BLOQUEO DE FECHAS EN EL CALENDARIO ---
        hoy = timezone.now().date()
        min_date = hoy + timedelta(days=4)
        max_date = hoy + timedelta(days=30)
        
        # Le decimos al input de HTML cuál es la fecha mínima y máxima permitida
        self.fields['fecha_entrega'].widget.attrs.update({
            'min': min_date.strftime('%Y-%m-%d'),
            'max': max_date.strftime('%Y-%m-%d')
        })
        # -------------------------------------------------

        # Lógica para mostrar solo nombre o nombre de empresa
        opciones_entidad = []
        if self.user and self.user.is_authenticated:
            nombre_usuario = self.user.get_full_name() or self.user.username
            opciones_entidad.append((nombre_usuario, nombre_usuario))
            
            if hasattr(self.user, 'perfil') and self.user.perfil.empresa:
                nombre_empresa = self.user.perfil.empresa.nombre
                opciones_entidad.append((nombre_empresa, nombre_empresa))

            self.fields['nombre_entidad'] = forms.ChoiceField(
                choices=opciones_entidad,
                widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'})
            )
        else:
            self.fields['nombre_entidad'].widget = forms.TextInput(attrs={'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        
        for field in ['detalles_cantidades', 'detalles_transporte']:
            value = cleaned_data.get(field)
            if isinstance(value, str) and value:
                try:
                    cleaned_data[field] = json.loads(value)
                except json.JSONDecodeError:
                    cleaned_data[field] = {}
            elif not value:
                cleaned_data[field] = {}

        # Auto-marcar los checks en base a si se enviaron datos en los JSON
        cleaned_data['requiere_productos'] = bool(cleaned_data.get('detalles_cantidades'))
        cleaned_data['requiere_transporte'] = bool(cleaned_data.get('detalles_transporte'))

        fecha = cleaned_data.get('fecha_entrega')
        if fecha:
            hoy = timezone.now().date()
            if fecha < hoy + timedelta(days=4):
                self.add_error('fecha_entrega', "La fecha debe tener al menos 4 días de antelación.")
            elif fecha > hoy + timedelta(days=30):
                self.add_error('fecha_entrega', "La fecha no puede superar el mes de antelación (máximo 30 días).")
        
        return cleaned_data