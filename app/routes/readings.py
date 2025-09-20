"""
routes/readings.py
Endpoint para inserir leituras manualmente (e usado pelo job).
Após inserção chama pipeline de regras e ML.
"""
from fastapi import APIRouter, Depends, HTTPException
from ..schemas import ReadingIn
from .. import db, auth
from datetime import datetime
import uuid
from ..services import notification
from ..utils import apply_threshold_rules
import logging

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


@router.post("/", response_model=dict)
async def create_reading(body: ReadingIn, user=Depends(auth.get_current_user)):
    doc = body.dict()
    doc["_id"] = str(uuid.uuid4())
    doc["timestamp"] = doc["timestamp"]
    await db.db.readings.insert_one(doc)

    # Regras determinísticas
    alerts = await apply_threshold_rules(doc)

    # ML anomaly detection (import lazy para evitar circular imports)
    is_anom = False
    score = None
    try:
        from ..ml.model import detect_anomaly  # import lazy
        try:
            is_anom, score = await detect_anomaly(doc)
        except Exception as e:
            # Se o ML falhar em runtime, logamos e seguimos sem bloquear.
            logger.warning("Erro ao executar detect_anomaly: %s", e)
            is_anom, score = False, None
    except Exception as e:
        # Se não for possível importar (por ex. import circular), logamos e seguimos.
        logger.warning("Não foi possível importar app.ml.model.detect_anomaly: %s", e)
        is_anom, score = False, None

    if is_anom:
        alerts.append({"level": "warning", "message": "Anomalia detectada", "value": score})

    # Salvar alerts e notificar
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
        await notification.notify_alert(a_doc)
    return {"status": "ok"}
