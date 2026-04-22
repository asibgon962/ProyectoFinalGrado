from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/organizacion/<int:solicitud_id>/', consumers.ChatSolicitudConsumer.as_asgi()),
    path('ws/chat/mercado/<int:pedido_id>/', consumers.ChatMercadoConsumer.as_asgi()),
    path('ws/chat/mis-gestiones/<int:solicitud_id>/', consumers.ChatSolicitudConsumer.as_asgi()),
]
