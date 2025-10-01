"""
scripts/import_historical.py
Script para importar todos os dados históricos do ThingSpeak.
CORRIGIDO: Problemas de asyncio loop e importação
"""
import asyncio
import httpx
import sys
import os
from datetime import datetime
import uuid
import logging

# Adicionar o diretório pai ao path para importar os módulos do app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_existing_data(db):
    """Verifica quantos dados já existem no banco"""
    try:
        total_readings = await db.db.readings.count_documents({})
        readings_with_silo_1 = await db.db.readings.count_documents({"silo_id": "1"})
        
        logger.info(f"📊 Dados atuais no banco:")
        logger.info(f"   - Total de leituras: {total_readings}")
        logger.info(f"   - Leituras com silo_id='1': {readings_with_silo_1}")
        
        # Mostrar algumas leituras recentes
        recent_cursor = db.db.readings.find({"silo_id": "1"}).sort("timestamp", -1).limit(3)
        recent_readings = []
        async for reading in recent_cursor:
            recent_readings.append(reading)
            
        logger.info("📈 Leituras mais recentes (silo_id='1'):")
        for reading in recent_readings:
            logger.info(f"   - {reading['timestamp']}: {reading['temp_C']}°C, {reading['rh_pct']}%")
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar dados existentes: {e}")

async def import_historical_data():
    """Importa dados históricos do ThingSpeak"""
    try:
        # ✅ CORREÇÃO: Importar dentro da função async
        from app import db, config
        
        # Inicializar o banco de dados
        db.init_db()
        
        # Verificar dados existentes antes da importação
        await check_existing_data(db)
        
        # Configurações do ThingSpeak
        channel_id = 3093339  # ID do canal no ThingSpeak
        read_key = "NXK09577J86GKO98"  # Sua chave de leitura
        silo_id = "1"  # ID do silo no seu sistema
        
        # URL para buscar todos os dados
        url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_key}"
        
        logger.info(f"📥 Importando dados históricos do canal {channel_id}")
        
        async with httpx.AsyncClient() as client:
            r = await client.get(url, timeout=30.0)
        
        if r.status_code != 200:
            logger.error(f"❌ Erro ao buscar dados: Status {r.status_code}")
            return
        
        data = r.json()
        feeds = data.get("feeds", [])
        logger.info(f"📊 Encontrados {len(feeds)} registros para importar")
        
        inserted_count = 0
        error_count = 0
        skipped_count = 0
        
        # Inserir todos os dados no MongoDB
        for f in feeds:
            try:
                # Tratar campos que podem estar vazios
                temp_val = f.get("field1")
                rh_val = f.get("field2")
                co2_val = f.get("field3")
                mq2_val = f.get("field4")
                
                # Pular se os campos principais estiverem vazios
                if temp_val is None or rh_val is None:
                    skipped_count += 1
                    continue
                
                # Criar documento
                doc = {
                    "_id": str(uuid.uuid4()),
                    "device_id": "1",
                    "timestamp": datetime.strptime(f.get("created_at"), "%Y-%m-%dT%H:%M:%SZ"),
                    "temp_C": float(temp_val or 0.0),
                    "rh_pct": float(rh_val or 0.0),
                    "co2_ppm_est": float(co2_val or 0.0),
                    "mq2_raw": int(mq2_val or 0),
                    "device_status": "ok",
                    "silo_id": silo_id
                }
                
                # Verificar se já existe antes de inserir (baseado em timestamp e valores)
                existing = await db.db.readings.find_one({
                    "device_id": doc["device_id"],
                    "timestamp": doc["timestamp"],
                    "temp_C": doc["temp_C"]
                })
                
                if not existing:
                    await db.db.readings.insert_one(doc)
                    inserted_count += 1
                    
                    if inserted_count % 50 == 0:  # Log a cada 50 registros
                        logger.info(f"📥 Progresso: {inserted_count} registros inseridos")
                else:
                    skipped_count += 1
                        
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Log apenas os primeiros 5 erros
                    logger.error(f"❌ Erro ao processar feed {f.get('entry_id')}: {e}")
                
        logger.info(f"✅ Importação histórica concluída!")
        logger.info(f"📊 Estatísticas:")
        logger.info(f"   - Registros inseridos: {inserted_count}")
        logger.info(f"   - Registros com erro: {error_count}")
        logger.info(f"   - Registros pulados: {skipped_count}")
        logger.info(f"   - Total processado: {len(feeds)}")
        
        # Verificar dados após importação
        await check_existing_data(db)
        
    except Exception as e:
        logger.error(f"❌ Erro na importação histórica: {e}")

def main():
    """Função principal para executar o script"""
    try:
        # ✅ CORREÇÃO: Usar asyncio.run() apenas uma vez
        asyncio.run(import_historical_data())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.info("Script concluído com sucesso")
        else:
            logger.error(f"❌ Erro de runtime: {e}")
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()