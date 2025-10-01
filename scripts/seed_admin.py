"""
scripts/seed_admin.py
Script para criar o primeiro admin. Uso:
INIT_ADMIN_SECRET=xxx python scripts/seed_admin.py --username admin --email a@b.com --password X --secret xxx
"""
import os
import argparse
import asyncio
import sys
from datetime import datetime
import uuid

# Adiciona o diretório pai ao path para importar os módulos do app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, auth, config

async def run(args):
    # Inicializar o banco de dados
    db.init_db()
    
    if config.INIT_ADMIN_SECRET is None:
        print("❌ ERRO: INIT_ADMIN_SECRET não configurado no ambiente.")
        print("   Defina a variável INIT_ADMIN_SECRET no .env")
        return
    
    if args.secret != config.INIT_ADMIN_SECRET:
        print("❌ ERRO: Secret inválido.")
        print(f"   Secret fornecido: {args.secret}")
        print(f"   Secret esperado: {config.INIT_ADMIN_SECRET}")
        return
    
    # Verificar se já existe algum admin
    existing_admins = await db.db.users.count_documents({"role": "admin"})
    if existing_admins > 0:
        print("⚠️  AVISO: Já existe um usuário admin no sistema.")
        response = input("Deseja criar outro admin mesmo assim? (s/N): ")
        if response.lower() != 's':
            print("Operação cancelada.")
            return
    
    # Criar o usuário admin
    user_doc = {
        "_id": str(uuid.uuid4()),
        "username": args.username,
        "email": args.email,
        "password_hash": auth.hash_password(args.password),
        "role": "admin",
        "created_at": datetime.utcnow(),
        "phone": args.phone or ""
    }
    
    try:
        await db.db.users.insert_one(user_doc)
        print(f"✅ Admin criado com sucesso!")
        print(f"   Username: {args.username}")
        print(f"   Email: {args.email}")
        print(f"   Role: admin")
        print(f"   ID: {user_doc['_id']}")
    except Exception as e:
        print(f"❌ Erro ao criar admin: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Criar usuário admin inicial")
    parser.add_argument("--username", required=True, help="Username do admin")
    parser.add_argument("--email", required=True, help="Email do admin")
    parser.add_argument("--password", required=True, help="Senha do admin")
    parser.add_argument("--phone", help="Telefone do admin (opcional)")
    parser.add_argument("--secret", required=True, help="Secret de inicialização (INIT_ADMIN_SECRET)")
    
    args = parser.parse_args()
    asyncio.run(run(args))