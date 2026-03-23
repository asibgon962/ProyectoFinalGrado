from django import forms
from .models import SolicitudServicio
from django.utils import timezone
from datetime import timedelta
import json

class SolicitudServicioForm(forms.ModelForm):
    tipo_servicio = forms.MultipleChoiceField(
        choices=SolicitudServicio.TIPO_CHOICES, 
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2', 
            'id': 'id_tipo_servicio'
        }),
        label="Tipos de Servicio"
    )

    detalles_cantidades = forms.CharField(widget=forms.HiddenInput(), required=False)
    detalles_transporte = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = SolicitudServicio
        fields = [
            'tipo_servicio', 
            'nombre_entidad', 
            'fecha_entrega', 
            'requiere_productos', 
            'observaciones', 
            'detalles_cantidades',
            'detalles_transporte'
        ]
        
        widgets = {
            'fecha_entrega': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nombre_entidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la empresa o evento'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'rows': 3,
                'placeholder': 'Detalles adicionales...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_servicio'].initial = []
        self.fields['detalles_cantidades'].initial = "{}"
        self.fields['detalles_transporte'].initial = "{}"

    def clean(self):
        cleaned_data = super().clean()
        
        # Limpieza de JSON para evitar errores de tipo string
        for field in ['detalles_cantidades', 'detalles_transporte']:
            value = cleaned_data.get(field)
            if isinstance(value, str) and value:
                try:
                    cleaned_data[field] = json.loads(value)
                except json.JSONDecodeError:
                    cleaned_data[field] = {}
            elif not value:
                cleaned_data[field] = {}

        # Validación de rango de fecha (Mínimo 4 días, Máximo 30 días)
        fecha = cleaned_data.get('fecha_entrega')
        if fecha:
            hoy = timezone.now().date()
            min_fecha = hoy + timedelta(days=4)
            max_fecha = hoy + timedelta(days=30)
            
            if fecha < min_fecha:
                self.add_error('fecha_entrega', "La fecha debe tener al menos 4 días de antelación.")
            elif fecha > max_fecha:
                self.add_error('fecha_entrega', "La fecha no puede superar el mes de antelación (máximo 30 días).")
        
        return cleaned_data