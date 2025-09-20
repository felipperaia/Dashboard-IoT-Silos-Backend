"""
routes/users.py
CRUD simples de usuários. Proteção básica por role.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..schemas import UserCreate, UserOut
from .. import db, auth
from datetime import datetime
import uuid

router = APIRouter()

def admin_required(user=Depends(auth.get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return user

@router.get("/", response_model=List[UserOut])
async def list_users(_=Depends(admin_required)):
    cursor = db.db.users.find({})
    users = []
    async for u in cursor:
        users.append({
            "id": u["_id"],
            "username": u["username"],
            "email": u["email"],
            "role": u.get("role", "operator"),
            "created_at": u.get("created_at"),
            "phone": u.get("phone")
        })
    return users

@router.post("/", response_model=dict)
async def create_user(body: UserCreate, _=Depends(admin_required)):
    user_doc = {
        "_id": str(uuid.uuid4()),
        "username": body.username,
        "email": body.email,
        "password_hash": auth.hash_password(body.password),
        "role": body.role,
        "created_at": datetime.utcnow(),
        "phone": body.phone
    }
    await db.db.users.insert_one(user_doc)
    return {"id": user_doc["_id"]}
