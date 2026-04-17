from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from catalog.models import Plato  
from .forms import SolicitudServicioForm
from .models import SolicitudServicio, MensajeSolicitud, PedidoMercado

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
            
            # Asociar la organización si el usuario la seleccionó
            if getattr(request.user, 'organization', None):
                if form.cleaned_data.get('nombre_entidad') == request.user.organization.nombre:
                    solicitud.organizacion = request.user.organization
            
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

@login_required
def panel_organizacion(request, solicitud_id=None):
    # Obtenemos la organización del usuario logueado
    org = request.user.organization
    if not org:
        messages.warning(request, "No perteneces a ninguna organización.")
        return redirect('home')

    # Obtenemos todas las solicitudes de su empresa
    solicitudes = SolicitudServicio.objects.filter(organizacion=org).order_by('-fecha_entrega')
    pedidos_mercado = PedidoMercado.objects.filter(organizacion=org).order_by('-fecha_pedido')

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
        'pedidos_mercado': pedidos_mercado,
        'solicitud_activa': solicitud_activa,
        'mensajes': mensajes
    })

@login_required
def enviar_mensaje(request, solicitud_id):
    if request.method == 'POST':
        solicitud = get_object_or_404(SolicitudServicio, id=solicitud_id)
        texto = request.POST.get('mensaje', '').strip()
        vuelve_a = request.POST.get('vuelve_a')
        
        if texto and len(texto) > 1000:
            texto = texto[:1000]
        
        # Validación de seguridad: el usuario debe ser de la misma organización, el autor, o admin
        if ((solicitud.organizacion and solicitud.organizacion == getattr(request.user, 'organization', None)) or solicitud.usuario == request.user or request.user.is_staff) and texto:
            MensajeSolicitud.objects.create(
                solicitud=solicitud,
                usuario=request.user,
                texto=texto,
                es_admin=request.user.is_staff
            )
            
        if vuelve_a == 'mis_gestiones':
            return redirect('mis_gestiones_chat', solicitud_id=solicitud_id)
    return redirect('mi_organizacion_chat', solicitud_id=solicitud_id)

@login_required
def panel_organizacion_mercado(request, pedido_id=None):
    org = request.user.organization
    if not org:
        messages.warning(request, "No perteneces a ninguna organización.")
        return redirect('home')

    solicitudes = SolicitudServicio.objects.filter(organizacion=org).order_by('-fecha_entrega')
    pedidos_mercado = PedidoMercado.objects.filter(organizacion=org).order_by('-fecha_pedido')

    pedido_activo = None
    mensajes = []

    if pedido_id:
        pedido_activo = get_object_or_404(PedidoMercado, id=pedido_id, organizacion=org)
        mensajes = pedido_activo.mensajes.all()

    return render(request, 'perfil-organizacion.html', {
        'organizacion': org,
        'solicitudes': solicitudes,
        'pedidos_mercado': pedidos_mercado,
        'pedido_mercado_activo': pedido_activo,
        'mensajes': mensajes
    })

@login_required
def enviar_mensaje_mercado(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(PedidoMercado, id=pedido_id)
        texto = request.POST.get('mensaje', '').strip()
        
        if texto and len(texto) > 1000:
            texto = texto[:1000]
            
        from .models import MensajePedidoMercado
        # Validación: comprador, organización o admin
        if ((pedido.organizacion == getattr(request.user, 'organization', None)) or pedido.usuario == request.user or request.user.is_staff) and texto:
            MensajePedidoMercado.objects.create(
                pedido=pedido,
                usuario=request.user,
                texto=texto,
                es_admin=request.user.is_staff
            )
    return redirect('mi_mercado_chat', pedido_id=pedido_id)

@login_required
def mis_gestiones(request, solicitud_id=None):
    # Obtenemos todas las solicitudes del usuario
    solicitudes = SolicitudServicio.objects.filter(usuario=request.user).order_by('-fecha_entrega')

    solicitud_activa = None
    mensajes = []

    # Lógica para seleccionar qué chat mostrar
    if solicitud_id:
        solicitud_activa = get_object_or_404(SolicitudServicio, id=solicitud_id, usuario=request.user)
    elif solicitudes.exists():
        solicitud_activa = solicitudes.first()

    if solicitud_activa:
        mensajes = solicitud_activa.mensajes.all()

    return render(request, 'mis-gestiones.html', {
        'solicitudes': solicitudes,
        'solicitud_activa': solicitud_activa,
        'mensajes': mensajes
    })