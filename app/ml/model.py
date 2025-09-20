"""
ml/model.py
Treino e inferência de IsolationForest.
Armazena modelos em collection ml_models como bytes (pickle).
"""
import pickle
from sklearn.ensemble import IsolationForest
from .. import db
import numpy as np
from datetime import datetime, timedelta

MODEL_NAME = "isolation_v1"

async def _fetch_training_data(days=30):
    since = datetime.utcnow() - timedelta(days=days)
    cursor = db.db.readings.find({"timestamp": {"$gte": since}})
    X = []
    async for r in cursor:
        X.append([
            r.get("temp_C", 0.0),
            r.get("rh_pct", 0.0),
            r.get("co2_ppm_est", 0.0),
            r.get("mq2_raw", 0)
        ])
    return np.array(X) if X else np.empty((0,4))

async def retrain(days=30):
    X = await _fetch_training_data(days)
    if X.shape[0] < 10:
        return {"status": "not enough data"}
    model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    model.fit(X)
    payload = pickle.dumps(model)
    await db.db.ml_models.update_one({"name": MODEL_NAME}, {"$set": {"name": MODEL_NAME, "model": payload, "trained_at": datetime.utcnow()}}, upsert=True)
    return {"status": "ok", "trained_samples": int(X.shape[0])}

async def load_model():
    doc = await db.db.ml_models.find_one({"name": MODEL_NAME})
    if not doc:
        return None
    return pickle.loads(doc["model"])

async def detect_anomaly(reading: dict):
    model = await load_model()
    if not model:
        return False, None
    X = [[reading.get("temp_C",0), reading.get("rh_pct",0), reading.get("co2_ppm_est",0), reading.get("mq2_raw",0)]]
    score = model.decision_function(X)[0]
    pred = model.predict(X)[0]  # -1 anomaly, 1 normal
    is_anom = pred == -1
    return bool(is_anom), float(score)
