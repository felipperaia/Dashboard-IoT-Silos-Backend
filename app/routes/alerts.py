"""
routes/alerts.py
Listar alertas e marcar como acknowledged.
"""
from fastapi import APIRouter, Depends, HTTPException
from .. import db, auth
from typing import List
from ..schemas import AlertOut
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[dict])
async def list_alerts(_=Depends(auth.get_current_user)):
    cursor = db.db.alerts.find({}).sort("timestamp", -1).limit(100)
    res = []
    async for a in cursor:
        res.append(a)
    return res

@router.post("/ack/{alert_id}")
async def ack_alert(alert_id: str, user=Depends(auth.get_current_user)):
    await db.db.alerts.update_one({"_id": alert_id}, {"$set": {"acknowledged": True, "ack_by": user["_id"], "ack_at": datetime.utcnow()}})
    # Registrar auditoria (omissão por brevidade)
    return {"status": "ok"}
