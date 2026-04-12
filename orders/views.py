from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalog.models import Plato  
from .forms import SolicitudServicioForm

@login_required
def solicitar_servicio(request):
    # Excelente que filtres solo los disponibles
    platos = Plato.objects.filter(disponible=True)
    
    if request.method == 'POST':
        # CAMBIO CLAVE: Le pasamos 'user=request.user' al formulario
        form = SolicitudServicioForm(request.POST, user=request.user)
        
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user 
            
            # ELIMINADO: La conversión manual de 'tipo_servicio' ya no es necesaria.
            # MultiSelectField de tu modelo se encarga de guardar la lista correctamente.
            
            solicitud.save()
            form.save_m2m() 
            
            messages.success(request, "Enviado")
            return redirect('home')
        else:
            # Esto ayuda a debugear en la terminal si algo falla
            print("Errores en el formulario:", form.errors)
            messages.error(request, "Hay errores en el formulario. Revisa los campos.")
    else:
        # CAMBIO CLAVE: También pasamos el usuario cuando se carga el formulario vacío (GET)
        form = SolicitudServicioForm(user=request.user)
    
    return render(request, 'orders/solicitud_form.html', {
        'form': form, 
        'platos_disponibles': platos
    })