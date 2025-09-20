"""
services/thing_speak.py
Cliente simples para ThingSpeak: consulta feeds e converte para ReadingIn.
"""
import httpx
from .. import config, db
from datetime import datetime
import uuid

THINGSPEAK_URL = "https://api.thingspeak.com/channels/{channel}/feeds.json?api_key={key}&results=1"

async def fetch_and_store(channel_id: int, read_key: str, silo_id: str = None, device_id: str = None):
    url = THINGSPEAK_URL.format(channel=channel_id, key=read_key)
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=10.0)
    if r.status_code != 200:
        return
    data = r.json()
    feeds = data.get("feeds", [])
    if not feeds:
        return
    f = feeds[0]
    # Map fields -> readings
    try:
        doc = {
            "_id": str(uuid.uuid4()),
            "device_id": device_id or f.get("entry_id"),
            "timestamp": datetime.strptime(f.get("created_at"), "%Y-%m-%d %H:%M:%S"),
            "temp_C": float(f.get("field1") or 0.0),
            "rh_pct": float(f.get("field2") or 0.0),
            "co2_ppm_est": float(f.get("field3") or 0.0),
            "mq2_raw": int(f.get("field4") or 0),
            "device_status": "ok",
            "silo_id": silo_id
        }
    except Exception:
        return
    await db.db.readings.insert_one(doc)
    # Pós-processamento: regras + ML + notificações
    from ..utils import apply_threshold_rules
    from ..ml.model import detect_anomaly
    from ..services.notification import notify_alert
    alerts = await apply_threshold_rules(doc)
    is_anom, score = await detect_anomaly(doc)
    if is_anom:
        alerts.append({"level": "warning", "message": "Anomalia detectada (ML)", "value": score})
    for a in alerts:
        a_doc = {
            "_id": str(uuid.uuid4()),
            "silo_id": doc.get("silo_id"),
            "level": a.get("level", "critical"),
            "message": a.get("message"),
            "value": a.get("value"),
            "timestamp": datetime.utcnow(),
            "acknowledged": False,
        }
        await db.db.alerts.insert_one(a_doc)
        await notify_alert(a_doc)
