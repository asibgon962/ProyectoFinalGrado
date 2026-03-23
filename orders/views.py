from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalog.models import Plato  
from .forms import SolicitudServicioForm

@login_required
def solicitar_servicio(request):
    platos = Plato.objects.filter(disponible=True)
    
    if request.method == 'POST':
        form = SolicitudServicioForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user 
            
            # Convertimos ['EVENTO', 'TRANSPORTE'] en "EVENTO, TRANSPORTE"
            servicios_lista = form.cleaned_data.get('tipo_servicio')
            solicitud.tipo_servicio = ", ".join(servicios_lista)
            
            solicitud.save()
            form.save_m2m() 
            
            messages.success(request, "¡Solicitud enviada con éxito!")
            return redirect('home')
        else:
            # Esto ayuda a debugear en la terminal si algo falla
            print("Errores en el formulario:", form.errors)
            messages.error(request, "Hay errores en el formulario. Revisa los campos.")
    else:
        form = SolicitudServicioForm()
    
    return render(request, 'orders/solicitud_form.html', {
        'form': form, 
        'platos_disponibles': platos
    })