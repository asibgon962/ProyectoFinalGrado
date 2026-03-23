from django import forms
from .models import SolicitudServicio
from django.utils import timezone
from datetime import timedelta
import json

class SolicitudServicioForm(forms.ModelForm):
    # Campos ocultos para recibir los JSON desde el JavaScript
    detalles_cantidades = forms.CharField(widget=forms.HiddenInput(), required=False)
    detalles_transporte = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = SolicitudServicio
        # Eliminamos 'vehiculo_vip' porque ya no existe en el modelo
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
            'tipo_servicio': forms.SelectMultiple(attrs={'class': 'form-select select2', 'id': 'id_tipo_servicio'}),
            'nombre_entidad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la empresa o evento'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
                'rows': 3,
                'placeholder': 'Detalles adicionales o logística especial...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['requiere_productos'].initial = False

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get('fecha_entrega')
        tipo = cleaned_data.get('tipo_servicio')
        
        # 1. Validación de margen de fechas
        if fecha:
            hoy = timezone.now().date()
            if fecha < hoy + timedelta(days=4):
                self.add_error('fecha_entrega', "Mínimo 4 días de antelación.")
            elif fecha > hoy + timedelta(days=30):
                self.add_error('fecha_entrega', "Máximo 30 días de antelación.")

        # 2. Validación de Stock para múltiples vehículos
        transporte_json = cleaned_data.get('detalles_transporte')
        if tipo == 'TRANSPORTE' and transporte_json and fecha:
            try:
                seleccion = json.loads(transporte_json)
                for vehiculo, cantidad in seleccion.items():
                    # Contamos cuántas unidades de este vehículo específico hay ya reservadas ese día
                    reservas_del_dia = SolicitudServicio.objects.filter(
                        fecha_entrega=fecha
                    ).exclude(estado='CANCELADO')
                    
                    total_reservado = 0
                    for r in reservas_del_dia:
                        # Sumamos las cantidades del JSON de cada reserva existente
                        total_reservado += r.detalles_transporte.get(vehiculo, 0)

                    if total_reservado + int(cantidad) > 2:
                        raise forms.ValidationError(
                            f"Lo sentimos, solo quedan {2 - total_reservado} unidades de '{vehiculo}' para el día {fecha}."
                        )
            except json.JSONDecodeError:
                pass 
        
        return cleaned_data