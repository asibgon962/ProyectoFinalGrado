import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def formato_europeo(valor):
    """Formatea un número al estilo europeo: 26.200.000,00"""
    try:
        # "{:,.2f}" → "26,200,000.00" (estilo anglosajón)
        anglosajón = "{:,.2f}".format(float(valor))
        # Swap: , ↔ .  (primero a placeholder X, luego swap)
        europeo = anglosajón.replace(',', 'X').replace('.', ',').replace('X', '.')
        return europeo
    except Exception:
        return str(valor)


def send_discord_notification(webhook_type, title, description, fields=None, url=None):
    """
    Envía una notificación a Discord usando Webhooks.
    webhook_type: 'servicios' o 'mn'
    """
    # Intentar obtener la URL del webhook desde settings o env
    webhook_url = None
    if webhook_type == 'servicios':
        webhook_url = getattr(settings, 'DISCORD_WEBHOOK_SERVICIOS', None)
    elif webhook_type == 'mn':
        webhook_url = getattr(settings, 'DISCORD_WEBHOOK_MN', None)

    if not webhook_url:
        logger.warning(f"Discord Webhook para '{webhook_type}' no configurado. Saltando notificación.")
        return False

    # Configuración del color (Dorado para MN, Azul para Servicios)
    color = 0xD4AF37 if webhook_type == 'mn' else 0x3498db

    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "fields": fields or [],
            "footer": {
                "text": "Sistema de Notificaciones Centro de Control"
            },
            "timestamp": None # Discord lo pondrá automáticamente si se envía vacío o se puede usar datetime.now().isoformat()
        }]
    }

    if url:
        payload["embeds"][0]["url"] = url

    try:
        response = requests.post(
            webhook_url, 
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Error enviando notificación a Discord: {e}")
        return False
