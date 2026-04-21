from users.models import MensajeContacto
from orders.models import SolicitudServicio, PedidoMercado

def admin_notifications(request):
    """
    Inyecta el número de notificaciones no leídas en el panel de administrador.
    Solo se ejecuta o devuelve datos si el usuario tiene permisos (is_staff).
    """
    if request.user.is_authenticated and request.user.is_staff:
        # Mensajes de contacto no contestados
        mensajes_contacto = MensajeContacto.objects.filter(contestado=False).order_by('-fecha_envio')
        num_mensajes_contacto = mensajes_contacto.count()

        # Solicitudes de servicio pendientes
        solicitudes_servicio = SolicitudServicio.objects.filter(estado='PENDIENTE').order_by('-fecha_entrega')
        num_solicitudes = solicitudes_servicio.count()

        # Pedidos del Mercado Negro pendientes
        pedidos_mercado = PedidoMercado.objects.filter(estado='PENDIENTE').order_by('-fecha_pedido')
        num_pedidos = pedidos_mercado.count()

        total_notifications = num_mensajes_contacto + num_solicitudes + num_pedidos

        # Solo queremos mostrar quizás las últimas 5 notificaciones de cada en el dropdown
        # O podemos pasarlas todas y que el front limite
        return {
            'admin_notifications_count': total_notifications,
            'admin_mensajes_contacto': mensajes_contacto[:5],
            'admin_solicitudes': solicitudes_servicio[:5],
            'admin_pedidos': pedidos_mercado[:5],
        }
    return {}
