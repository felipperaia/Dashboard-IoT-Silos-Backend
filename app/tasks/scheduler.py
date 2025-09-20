"""
tasks/scheduler.py
Inicia APScheduler para rodar job de ingestão ThingSpeak a cada N minutos.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .. import config
from ..services.thing_speak import fetch_and_store
from .. import db
import asyncio

def start_scheduler(app):
    scheduler = AsyncIOScheduler()
    async def job():
        # Para cada channel mapeado em config.THINGSPEAK_CHANNELS
        for silo_key, channel in config.THINGSPEAK_CHANNELS.items():
            read_key = config.THINGSPEAK_API_KEYS.get(silo_key)
            # Mapear silo_key para silo_id na collection silos (device_id ou nome)
            silo = await db.db.silos.find_one({"name": silo_key})
            silo_id = silo["_id"] if silo else None
            device_id = silo.get("device_id") if silo else None
            await fetch_and_store(channel, read_key, silo_id=silo_id, device_id=device_id)
    scheduler.add_job(lambda: asyncio.create_task(job()), "interval", minutes=5)
    scheduler.start()
