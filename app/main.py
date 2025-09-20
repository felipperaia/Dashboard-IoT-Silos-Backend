from fastapi import FastAPI
import logging

# importar routers existentes na pasta routes
from .routes import auth, users, silos, readings, alerts, notifications

app = FastAPI()
logger = logging.getLogger("uvicorn.error")

# Registrar routers principais
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(silos.router, prefix="/api/silos", tags=["silos"])
app.include_router(readings.router, prefix="/api/readings", tags=["readings"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

# Tentar registrar router ML de forma condicional:
# 1) tenta importar app.routes.ml (se existe uma rota dedicada em routes/)
# 2) senao tenta importar app.ml (caso o package ml defina um router)
# Se nada existir, registra nada e apenas loga.
try:
    try:
        # se houver um modulo app.routes.ml (preferivel), importe-o
        from .routes import ml as ml_routes
        if hasattr(ml_routes, "router"):
            app.include_router(ml_routes.router, prefix="/api/ml", tags=["ml"])
        else:
            logger.info("app.routes.ml foi importado mas nao tem atributo 'router'; pulando.")
    except Exception:
        # fallback para package app.ml
        from . import ml as ml_pkg
        if hasattr(ml_pkg, "router"):
            app.include_router(ml_pkg.router, prefix="/api/ml", tags=["ml"])
        else:
            logger.info("app.ml importado mas nao tem atributo 'router'; pulando registro do router ML.")
except Exception as e:
    logger.warning("Nao foi possivel registrar router ML: %s", e)
