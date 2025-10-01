"""
routes/silos.py
Endpoints para listar e editar silos e seus settings.
CORRIGIDO: Garantir que _id seja convertido para string
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas import SiloCreate, SiloSettings
from .. import db, auth
from datetime import datetime
import uuid

router = APIRouter()

@router.get("/", response_model=List[dict])
async def list_silos(user=Depends(auth.get_current_user)):
    """
    Lista todos os silos.
    CORREÇÃO: Converter _id para string e garantir estrutura consistente
    """
    cursor = db.db.silos.find({})
    res = []
    async for s in cursor:
        # ✅ CORREÇÃO: Converter ObjectId para string e garantir estrutura consistente
        silo_data = {
            "_id": str(s["_id"]),
            "name": s.get("name", ""),
            "device_id": s.get("device_id", ""),
            "location": s.get("location", {}),
            "settings": s.get("settings", {}),
            "created_at": s.get("created_at"),
            "responsible": s.get("responsible", {})
        }
        res.append(silo_data)
    print(f"✅ Silos retornados: {len(res)}")  # Debug
    return res

@router.post("/", response_model=dict)
async def create_silo(body: SiloCreate, user=Depends(auth.get_current_user)):
    # somente admin
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    
    doc = {
        "_id": str(uuid.uuid4()),
        "name": body.name,
        "device_id": body.device_id,
        "location": body.location or {},
        "settings": body.settings.dict() if body.settings else {},
        "created_at": datetime.utcnow(),
        "responsible": {}
    }
    
    result = await db.db.silos.insert_one(doc)
    print(f"✅ Silo criado: {doc['_id']}")  # Debug
    return {"id": doc["_id"], "status": "created"}

@router.put("/{silo_id}/settings", response_model=dict)
async def update_settings(silo_id: str, settings: SiloSettings, user=Depends(auth.get_current_user)):
    if user.get("role") not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="Admin or operator required")
    
    result = await db.db.silos.update_one(
        {"_id": silo_id}, 
        {"$set": {"settings": settings.dict()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Silo not found")
    
    return {"status": "ok", "message": "Settings updated"}