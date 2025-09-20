"""
routes/silos.py
Endpoints para listar e editar silos e seus settings.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas import SiloCreate, SiloSettings
from .. import db, auth
from datetime import datetime
import uuid

router = APIRouter()

@router.get("/", response_model=List[dict])
async def list_silos(_=Depends(auth.get_current_user)):
    cursor = db.db.silos.find({})
    res = []
    async for s in cursor:
        res.append(s)
    return res

@router.post("/", response_model=dict)
async def create_silo(body: SiloCreate, user=Depends(auth.get_current_user)):
    # somente admin
    if user.get("role") != "admin":
        raise HTTPException(status_code=403)
    doc = {
        "_id": str(uuid.uuid4()),
        "name": body.name,
        "device_id": body.device_id,
        "location": body.location,
        "settings": body.settings.dict() if body.settings else {},
        "created_at": datetime.utcnow(),
        "responsible": {}
    }
    await db.db.silos.insert_one(doc)
    return {"id": doc["_id"]}

@router.put("/{silo_id}/settings", response_model=dict)
async def update_settings(silo_id: str, settings: SiloSettings, user=Depends(auth.get_current_user)):
    if user.get("role") not in ("admin", "operator"):
        raise HTTPException(status_code=403)
    await db.db.silos.update_one({"_id": silo_id}, {"$set": {"settings": settings.dict()}})
    return {"status": "ok"}
