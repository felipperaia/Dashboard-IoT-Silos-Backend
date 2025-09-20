"""
services/notification.py
Enviar notificações por Telegram e Web Push (pywebpush).
NOTA: suporte a SMS via email-to-sms foi DESABILITADO (comentado) — não será usado
a menos que você reative explicitamente e configure credenciais SMTP.
"""
import httpx
from .. import config, db
import asyncio
from typing import Dict, Any
from pywebpush import webpush, WebPushException
import json
import logging

logger = logging.getLogger("notification")

async def send_telegram(chat_id: str, text: str):
    if not config.TELEGRAM_BOT_TOKEN:
        logger.debug("Telegram token não configurado; pulando envio Telegram")
        return
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": text})

def _vapid_auth():
    # Retorna dict com chave privada/publica se disponíveis
    if not config.VAPID_PRIVATE_KEY or not config.VAPID_PUBLIC_KEY:
        return None
    return {
        "vapid_private_key": config.VAPID_PRIVATE_KEY,
        "vapid_claims": {"sub": f"mailto:{config.SMTP_USER or 'no-reply@example.com'}"}
    }

async def send_webpush(subscription_info: Dict[str, Any], payload: str):
    """
    Envia Web Push usando pywebpush. subscription_info deve ser o objeto retornado
    por PushManager.subscribe() (endpoint + keys.p256dh + keys.auth).
    """
    vapid = _vapid_auth()
    if not vapid:
        logger.warning("VAPID keys não configuradas; pulando envio WebPush")
        return
    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=vapid["vapid_private_key"],
            vapid_claims=vapid["vapid_claims"]
        )
    except WebPushException as ex:
        logger.exception("Falha ao enviar webpush: %s", ex)
        # Se for 410/404 do endpoint remova a subscription (tratada no caller)
        raise

# -----------------------------------------------------------
# SMS fallback: função comentada / desabilitada por padrão.
# Para reativar:
#  - configurar SMTP_* no .env
#  - implementar segurança e validação adicional
# -----------------------------------------------------------
async def send_sms_via_email(phone: str, carrier_gateway: str, subject: str, body: str):
    """
    FUNÇÃO DESABILITADA:
    Implementação do envio de SMS via gateway de email foi intencionalmente
    desativada e comentada. Se você precisar habilitar, implemente com cautela:
    - valide phone e carrier_gateway,
    - configure SMTP_* no .env,
    - habilite TLS/STARTTLS,
    - monitore limites de envio.
    """
    logger.info("send_sms_via_email está desabilitado. Para habilitar, edite services/notification.py e configure SMTP_* no .env.")
    return

# -----------------------------------------------------------
# Notify pipeline (usa Telegram e WebPush; não usa SMS por padrão)
# -----------------------------------------------------------
async def notify_alert(alert: Dict[str, Any]):
    """
    Busca responsáveis do silo e envia notificações:
    - Telegram para silo.responsible.telegram_chat_id
    - WebPush para subscriptions relacionadas ao silo (campo silo_id) ou globais
    """
    silo = await db.db.silos.find_one({"_id": alert["silo_id"]})
    silo_name = silo.get("name") if silo else "Silo"
    text = f"[{alert['level'].upper()}] {silo_name}: {alert['message']} (valor={alert.get('value')})"

    # Telegram
    chat_id = silo.get("responsible", {}).get("telegram_chat_id") if silo else None
    if chat_id:
        await send_telegram(chat_id, text)

    # WebPush: buscar subscriptions específicas para este silo + globais (silo_id=null)
    subs_cursor = db.db.push_subscriptions.find({"$or": [{"silo_id": alert["silo_id"]}, {"silo_id": None}]})
    async for sub in subs_cursor:
        try:
            subscription_info = {
                "endpoint": sub["endpoint"],
                "keys": sub.get("keys", {})
            }
            # pywebpush é síncrono, executamos no executor para não bloquear loop async
            await asyncio.get_event_loop().run_in_executor(None, lambda: send_webpush_sync(subscription_info, json.dumps({"title": "Silo Monitor", "body": text})))
        except Exception as e:
            logger.exception("Erro enviando webpush; removendo subscription possivelmente inválida: %s", e)
            try:
                await db.db.push_subscriptions.delete_one({"_id": sub["_id"]})
            except Exception:
                pass
    return

# helper síncrono para chamar webpush dentro do executor (pywebpush é síncrono)
def send_webpush_sync(subscription_info, payload):
    vapid = _vapid_auth()
    if not vapid:
        return
    webpush(subscription_info=subscription_info, data=payload, vapid_private_key=vapid["vapid_private_key"], vapid_claims=vapid["vapid_claims"])
