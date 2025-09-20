"""
scripts/seed_admin.py
Script para criar o primeiro admin. Uso:
INIT_ADMIN_SECRET=xxx python scripts/seed_admin.py --username admin --email a@b.com --password X
"""
import os
import argparse
import asyncio
from backend.app import db, auth, config
from datetime import datetime
import uuid

async def run(args):
    db.init_db()
    if config.INIT_ADMIN_SECRET is None:
        print("INIT_ADMIN_SECRET não configurado. Abortando.")
        return
    if args.secret != config.INIT_ADMIN_SECRET:
        print("Secret inválido.")
        return
    existing = await db.db.users.count_documents({"role": "admin"})
    if existing > 0:
        print("Admin já existe. Abortando.")
        return
    user_doc = {
        "_id": str(uuid.uuid4()),
        "username": args.username,
        "email": args.email,
        "password_hash": auth.hash_password(args.password),
        "role": "admin",
        "created_at": datetime.utcnow(),
        "phone": args.phone
    }
    await db.db.users.insert_one(user_doc)
    print("Admin criado:", user_doc["username"])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--phone", required=False)
    parser.add_argument("--secret", required=True)
    args = parser.parse_args()
    asyncio.run(run(args))
