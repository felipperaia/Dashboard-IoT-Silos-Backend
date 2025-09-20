# ARCHITECTURE

Fluxo:
ThingSpeak -> Job APScheduler (backend) -> transforma -> readings collection (MongoDB)
-> pipeline de regras determinísticas + ML (IsolationForest)
-> alerts collection -> NotificationService (Telegram/WebPush/SMTP)
Frontend (PWA) consulta APIs e recebe WebPush / websocket (não implementado fully no exemplo).

Coleções principais: users, silos, readings, alerts, ml_models.
