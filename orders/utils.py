import hmac
import hashlib
import requests
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


BASE_URL = "https://koienterprise.onrender.com"


ESTADOS_ACCION = {
    'solicitud': [
        ('ACEPTADO',   '✅ Aceptar'),
        ('EN_CAMINO',  '🚚 En reparto'),
        ('COMPLETADO', '✔️ Completado'),
        ('CANCELADO',  '❌ Cancelar'),
    ],
    'mercado': [
        ('ACEPTADO',   '✅ Aceptar'),
        ('EN_CAMINO',  '🚚 En reparto'),
        ('COMPLETADO', '✔️ Completado'),
        ('CANCELADO',  '❌ Cancelar'),
    ],
}




def _firma_mensaje(tipo: str, objeto_id: int, nuevo_estado: str) -> str:
    """Cadena normalizada que se firma con HMAC."""
    return f"{tipo}:{objeto_id}:{nuevo_estado}"


def generar_token_accion(tipo: str, objeto_id: int, nuevo_estado: str) -> str:
    """Devuelve un token HMAC-SHA256 (hex) para el cambio de estado solicitado."""
    mensaje = _firma_mensaje(tipo, objeto_id, nuevo_estado).encode()
    clave   = settings.SECRET_KEY.encode()
    return hmac.new(clave, mensaje, hashlib.sha256).hexdigest()


def verificar_token_accion(tipo: str, objeto_id: int, nuevo_estado: str, token: str) -> bool:
    """Verifica que el token recibido sea válido (comparación segura)."""
    esperado = generar_token_accion(tipo, objeto_id, nuevo_estado)
    return hmac.compare_digest(esperado, token)


def generar_links_accion(tipo: str, objeto_id: int) -> list[dict]:
    """
    Devuelve una lista de dicts {'label': str, 'url': str}
    listos para añadir como campos al embed de Discord.
    """
    estados = ESTADOS_ACCION.get(tipo, [])
    links = []
    for estado_key, label in estados:
        token = generar_token_accion(tipo, objeto_id, estado_key)
        url = (
            f"{BASE_URL}/orders/accion/{tipo}/{objeto_id}/{estado_key}/"
            f"?token={token}"
        )
        links.append({'label': label, 'url': url})
    return links




def formato_europeo(valor):
    """Formatea un número al estilo europeo: 26.200.000,00"""
    try:
        anglosajón = "{:,.2f}".format(float(valor))
        europeo = anglosajón.replace(',', 'X').replace('.', ',').replace('X', '.')
        return europeo
    except Exception:
        return str(valor)




def send_discord_notification(webhook_type, title, description, fields=None, url=None):
    """
    Envía una notificación a Discord usando Webhooks.
    webhook_type: 'servicios' o 'mn'
    """
    webhook_url = None
    if webhook_type == 'servicios':
        webhook_url = getattr(settings, 'DISCORD_WEBHOOK_SERVICIOS', None)
    elif webhook_type == 'mn':
        webhook_url = getattr(settings, 'DISCORD_WEBHOOK_MN', None)

    if not webhook_url:
        logger.warning(f"Discord Webhook para '{webhook_type}' no configurado. Saltando notificación.")
        return False

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
            "timestamp": None
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
