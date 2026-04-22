import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SolicitudServicio, MensajeSolicitud, PedidoMercado, MensajePedidoMercado
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatSolicitudConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.solicitud_id = self.scope['url_route']['kwargs']['solicitud_id']
        self.room_group_name = f'chat_solicitud_{self.solicitud_id}'

        # Unirse a la sala de grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Abandonar sala
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recibir mensaje del WebSocket (del navegador)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        user = self.scope['user']
        if not user.is_authenticated:
            return

        user_id = user.id
        es_admin = user.is_staff

        # Guardar en base de datos (esto disparará la señal post_save que hace el broadcast)
        await self.save_message(user_id, self.solicitud_id, message, es_admin)

    # Recibir el mensaje del grupo de canales e inyectarlo al websocket
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'es_admin': event['es_admin'],
            'fecha_envio': event['fecha_envio']
        }))

    @database_sync_to_async
    def save_message(self, user_id, solicitud_id, message, es_admin):
        solicitud = SolicitudServicio.objects.get(id=solicitud_id)
        user = User.objects.get(id=user_id)
        return MensajeSolicitud.objects.create(
            solicitud=solicitud,
            usuario=user,
            texto=message,
            es_admin=es_admin
        )


class ChatMercadoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.pedido_id = self.scope['url_route']['kwargs']['pedido_id']
        self.room_group_name = f'chat_mercado_{self.pedido_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        user = self.scope['user']
        if not user.is_authenticated:
            return
            
        user_id = user.id
        es_admin = user.is_staff

        # Guardar (dispara la señal)
        await self.save_message(user_id, self.pedido_id, message, es_admin)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'es_admin': event['es_admin'],
            'fecha_envio': event['fecha_envio']
        }))

    @database_sync_to_async
    def save_message(self, user_id, pedido_id, message, es_admin):
        pedido = PedidoMercado.objects.get(id=pedido_id)
        user = User.objects.get(id=user_id)
        return MensajePedidoMercado.objects.create(
            pedido=pedido,
            usuario=user,
            texto=message,
            es_admin=es_admin
        )
