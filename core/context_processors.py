from users.models import MensajeContacto
from orders.models import SolicitudServicio, PedidoMercado, MensajeSolicitud, MensajePedidoMercado
from django.db.models import Q

def admin_notifications(request):
    """
    Inyecta el número de notificaciones no leídas en el panel de administrador y web.
    """
    data = {}
    
    if not request.user.is_authenticated:
        return data

    # --- NOTIFICACIONES PARA ADMIN (STAFF) ---
    if request.user.is_staff:
        # Mensajes de contacto no contestados
        mensajes_contacto = MensajeContacto.objects.filter(contestado=False).order_by('-fecha_envio')
        num_mensajes_contacto = mensajes_contacto.count()

        # Solicitudes de servicio pendientes
        solicitudes_servicio = SolicitudServicio.objects.filter(estado='PENDIENTE').order_by('-fecha_entrega')
        num_solicitudes = solicitudes_servicio.count()

        # Pedidos del Mercado Negro pendientes
        pedidos_mercado = PedidoMercado.objects.filter(estado='PENDIENTE').order_by('-fecha_pedido')
        num_pedidos = pedidos_mercado.count()

        # --- CHATS NO LEÍDOS (Novedades de usuarios) ---
        # Contamos cuántas solicitudes tienen mensajes de usuario sin leer
        chats_solicitud_unread = SolicitudServicio.objects.filter(
            mensajes__es_admin=False, 
            mensajes__leido=False
        ).distinct().count()

        # Contamos cuántos pedidos tienen mensajes de usuario sin leer
        chats_mercado_unread = PedidoMercado.objects.filter(
            mensajes__es_admin=False, 
            mensajes__leido=False
        ).distinct().count()

        num_chats_admin = chats_solicitud_unread + chats_mercado_unread

        total_notifications = num_mensajes_contacto + num_solicitudes + num_pedidos + num_chats_admin

        data.update({
            'admin_notifications_count': total_notifications,
            'admin_mensajes_contacto': mensajes_contacto[:5],
            'admin_solicitudes': solicitudes_servicio[:5],
            'admin_pedidos': pedidos_mercado[:5],
            'num_chats_admin': num_chats_admin, # Para el badge de "Chat en Vivo"
        })

    # --- NOTIFICACIONES PARA USUARIO NORMAL ---
    # Mensajes de admin sin leer en sus gestiones o las de su organización
    user_q_sol = Q(usuario=request.user)
    user_q_ped = Q(usuario=request.user)
    
    if hasattr(request.user, 'organization') and request.user.organization:
        user_q_sol |= Q(organizacion=request.user.organization)
        user_q_ped |= Q(organizacion=request.user.organization)

    chats_solicitud_user_unread = SolicitudServicio.objects.filter(
        user_q_sol,
        mensajes__es_admin=True,
        mensajes__leido=False
    ).distinct().count()

    chats_mercado_user_unread = PedidoMercado.objects.filter(
        user_q_ped,
        mensajes__es_admin=True,
        mensajes__leido=False
    ).distinct().count()

    data['num_chats_user'] = chats_solicitud_user_unread + chats_mercado_user_unread

    return data
