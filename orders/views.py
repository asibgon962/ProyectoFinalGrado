from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalog.models import Plato  
from .forms import SolicitudServicioForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import SolicitudServicio, MensajeSolicitud

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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SolicitudServicio, MensajeSolicitud

@login_required
def panel_organizacion(request, solicitud_id=None):
    # Obtenemos la organización del usuario logueado
    org = request.user.organization
    if not org:
        messages.warning(request, "No perteneces a ninguna organización.")
        return redirect('home')

    # Obtenemos todas las solicitudes de su empresa
    solicitudes = SolicitudServicio.objects.filter(organizacion=org).order_by('-fecha_entrega')

    solicitud_activa = None
    mensajes = []

    # Lógica para seleccionar qué chat mostrar
    if solicitud_id:
        solicitud_activa = get_object_or_404(SolicitudServicio, id=solicitud_id, organizacion=org)
    elif solicitudes.exists():
        solicitud_activa = solicitudes.first()

    if solicitud_activa:
        mensajes = solicitud_activa.mensajes.all()

    return render(request, 'perfil-organizacion.html', {
        'organizacion': org,
        'solicitudes': solicitudes,
        'solicitud_activa': solicitud_activa,
        'mensajes': mensajes
    })

@login_required
def enviar_mensaje(request, solicitud_id):
    if request.method == 'POST':
        solicitud = get_object_or_404(SolicitudServicio, id=solicitud_id)
        texto = request.POST.get('mensaje')
        
        # Validación de seguridad: el usuario debe ser de la misma organización
        if solicitud.organizacion == request.user.organization and texto:
            MensajeSolicitud.objects.create(
                solicitud=solicitud,
                usuario=request.user,
                texto=texto,
                es_admin=request.user.is_staff
            )
    return redirect('mi_organizacion_chat', solicitud_id=solicitud_id)