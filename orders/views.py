from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from .forms import SolicitudServicioForm
from .models import SolicitudServicio, MensajeSolicitud, PedidoMercado
from .utils import verificar_token_accion
from catalog.models import Plato

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

@staff_member_required
def admin_chat_dashboard(request, chat_type=None, object_id=None):
    # Obtenemos todas las gestiones para el listado lateral
    solicitudes = SolicitudServicio.objects.all().order_by('-fecha_entrega')
    pedidos_mercado = PedidoMercado.objects.all().order_by('-fecha_pedido')

    chat_activo = None
    mensajes = []

    if chat_type == 'solicitud' and object_id:
        chat_activo = get_object_or_404(SolicitudServicio, id=object_id)
        mensajes = chat_activo.mensajes.all()
    elif chat_type == 'mercado' and object_id:
        chat_activo = get_object_or_404(PedidoMercado, id=object_id)
        mensajes = chat_activo.mensajes.all()

    return render(request, 'admin-chat.html', {
        'solicitudes': solicitudes,
        'pedidos_mercado': pedidos_mercado,
        'chat_activo': chat_activo,
        'chat_type': chat_type,
        'mensajes': mensajes
    })


# ── Acción de cambio de estado desde link firmado (Discord) ───────────────────

TIPOS_VALIDOS = {
    'solicitud': {
        'model': SolicitudServicio,
        'estados': ['ACEPTADO', 'EN_CAMINO', 'COMPLETADO', 'CANCELADO'],
        'label': 'Solicitud de Servicio',
    },
    'mercado': {
        'model': PedidoMercado,
        'estados': ['ACEPTADO', 'EN_CAMINO', 'COMPLETADO', 'CANCELADO'],
        'label': 'Pedido Mercado Negro',
    },
}

def accion_estado(request, tipo, objeto_id, nuevo_estado):
    """
    Cambia el estado de un pedido/solicitud mediante un link firmado con HMAC.
    No requiere autenticación; la seguridad la garantiza el token.
    GET /orders/accion/<tipo>/<objeto_id>/<nuevo_estado>/?token=<hmac>
    """
    # 1. Validar tipo y estado
    config = TIPOS_VALIDOS.get(tipo)
    if not config:
        return HttpResponseBadRequest("Tipo de objeto no reconocido.")

    if nuevo_estado not in config['estados']:
        return HttpResponseBadRequest("Estado no válido.")

    # 2. Verificar token HMAC
    token = request.GET.get('token', '')
    if not verificar_token_accion(tipo, objeto_id, nuevo_estado, token):
        return HttpResponseForbidden("Token inválido o manipulado. Acceso denegado.")

    # 3. Obtener el objeto y aplicar el cambio
    Model = config['model']
    obj = get_object_or_404(Model, id=objeto_id)
    estado_anterior = obj.get_estado_display()
    obj.estado = nuevo_estado
    obj.save()

    # 4. Notificar a Discord el cambio de estado
    try:
        from .utils import send_discord_notification, generar_links_accion

        webhook_type = 'mn' if tipo == 'mercado' else 'servicios'

        # Emojis por estado
        EMOJI_ESTADO = {
            'ACEPTADO':   '✅',
            'EN_CAMINO':  '🚚',
            'COMPLETADO': '✔️',
            'CANCELADO':  '❌',
        }
        emoji = EMOJI_ESTADO.get(nuevo_estado, '🔄')

        title = f"{emoji} Estado Actualizado — {config['label']} #{objeto_id}"
        description = (
            f"El estado ha cambiado de **{estado_anterior}** "
            f"a **{obj.get_estado_display()}**."
        )

        # Construir campos con info del objeto
        fields = [
            {"name": "Estado anterior", "value": estado_anterior,          "inline": True},
            {"name": "Estado nuevo",    "value": obj.get_estado_display(), "inline": True},
        ]

        # Añadir nuevos links de acción para los estados restantes
        links = generar_links_accion(tipo, objeto_id)
        # Filtrar el estado actual de los links
        links_filtrados = [l for l in links if nuevo_estado not in l['url']]
        if links_filtrados:
            links_texto = "  ·  ".join(f"[{l['label']}]({l['url']})" for l in links_filtrados)
            fields.append({"name": "⚡ Otros cambios", "value": links_texto, "inline": False})

        send_discord_notification(webhook_type, title, description, fields)
    except Exception:
        pass  # Nunca bloquear la acción por un fallo de Discord

    # 5. Renderizar página de confirmación mínima
    return render(request, 'orders/accion_confirmada.html', {
        'tipo_label': config['label'],
        'objeto_id': objeto_id,
        'estado_anterior': estado_anterior,
        'nuevo_estado': obj.get_estado_display(),
    })