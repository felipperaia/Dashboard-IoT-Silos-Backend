"""
scripts/import_historical.py
Script para importar todos os dados históricos do ThingSpeak.
"""
import asyncio
import httpx
from app import config, db
from datetime import datetime
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def import_historical_data():
    # Configurações do ThingSpeak
    channel_id = 3082805  # ID do canal no ThingSpeak
    read_key = "2KX537GW7RZ2LQZQ"  # Sua chave de leitura
    silo_id = "1"  # ID do silo no seu sistema
    
    # URL para buscar todos os dados (sem limite de results)
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_key}"
    
    logger.info(f"Importando dados históricos do canal {channel_id}")
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=30.0)
        
        if r.status_code != 200:
            logger.error(f"Erro ao buscar dados: Status {r.status_code}")
            return
        
        data = r.json()
        feeds = data.get("feeds", [])
        logger.info(f"Encontrados {len(feeds)} registros para importar")
        
        # Inserir todos os dados no MongoDB
        for f in feeds:
            try:
                doc = {
                    "_id": str(uuid.uuid4()),
                    "device_id": silo_id,
                    "timestamp": datetime.strptime(f.get("created_at"), "%Y-%m-%dT%H:%M:%SZ"),
                    "temp_C": float(f.get("field1") or 0.0),
                    "rh_pct": float(f.get("field2") or 0.0),
                    "co2_ppm_est": float(f.get("field3") or 0.0),
                    "mq2_raw": int(f.get("field4") or 0),
                    "device_status": "ok",
                    "silo_id": silo_id
                }
                await db.db.readings.insert_one(doc)
                logger.info(f"Inserido registro {f['entry_id']}")
            except Exception as e:
                logger.error(f"Erro ao processar feed {f.get('entry_id')}: {e}")
                
        logger.info("Importação histórica concluída!")
        
    except Exception as e:
        logger.error(f"Erro na importação histórica: {e}")

if __name__ == "__main__":
    # Inicializar o banco de dados
    from app import db
    db.init_db()
    
    # Executar a importação
    asyncio.run(import_historical_data())