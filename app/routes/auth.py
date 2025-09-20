"""
routes/auth.py
Rotas: login, refresh, seed-admin, logout.
Modificadas para persistir refresh tokens (hashed) e permitir logout/revogação.
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from ..schemas import LoginIn, Token, UserCreate
from .. import db, auth, config
from datetime import datetime, timedelta
import uuid

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(data: LoginIn):
    user = await db.db.users.find_one({"username": data.username})
    if not user or not auth.verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access, refresh = auth.create_tokens(str(user["_id"]))
    # Armazenar refresh token hashed para maior segurança
    hashed = auth.pwd_context.hash(refresh)
    expires_at = datetime.utcnow() + timedelta(days=config.JWT_REFRESH_EXPIRE_DAYS)
    await db.db.refresh_tokens.update_one(
        {"user_id": str(user["_id"])},
        {"$set": {"user_id": str(user["_id"]), "token_hash": hashed, "expires_at": expires_at}},
        upsert=True
    )
    return {"access_token": access, "refresh_token": refresh}

@router.post("/refresh", response_model=Token)
async def refresh(token: str = Body(...)):
    try:
        payload = auth.jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh inválido")
    # Verifica token hashed salvo
    doc = await db.db.refresh_tokens.find_one({"user_id": str(user_id)})
    if not doc or not auth.pwd_context.verify(token, doc.get("token_hash", "")):
        raise HTTPException(status_code=401, detail="Refresh inválido ou revogado")
    # Rotaciona tokens: cria novos e atualiza hash
    access, new_refresh = auth.create_tokens(user_id)
    new_hashed = auth.pwd_context.hash(new_refresh)
    expires_at = datetime.utcnow() + timedelta(days=config.JWT_REFRESH_EXPIRE_DAYS)
    await db.db.refresh_tokens.update_one({"user_id": str(user_id)}, {"$set": {"token_hash": new_hashed, "expires_at": expires_at}})
    return {"access_token": access, "refresh_token": new_refresh}

@router.post("/logout")
async def logout(token: str = Body(...)):
    """
    Logout: revoga refresh token enviado pelo cliente.
    """
    try:
        payload = auth.jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
    except Exception:
        # Se o token inválido, tenta apenas remover qualquer refresh para segurança
        raise HTTPException(status_code=401, detail="Refresh inválido")
    # Remove refresh token entry (revoga)
    await db.db.refresh_tokens.delete_one({"user_id": str(user_id)})
    return {"status": "ok"}

@router.post("/seed-admin", summary="Criar admin inicial (apenas se nenhum existir)")
async def seed_admin(body: UserCreate = Body(...), secret: str = Body(...)):
    # Segurança: exige INIT_ADMIN_SECRET e somente se não existir admin
    if config.INIT_ADMIN_SECRET is None or secret != config.INIT_ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Secret inválido")
    existing = await db.db.users.count_documents({"role": "admin"})
    if existing > 0:
        raise HTTPException(status_code=400, detail="Admin já existe")
    user_doc = {
        "_id": str(uuid.uuid4()),
        "username": body.username,
        "email": body.email,
        "password_hash": auth.hash_password(body.password),
        "role": "admin",
        "created_at": datetime.utcnow(),
        "phone": body.phone
    }
    await db.db.users.insert_one(user_doc)
    return {"status": "ok"}
