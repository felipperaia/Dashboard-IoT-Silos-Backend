"""
schemas.py
Modelos Pydantic para requests/responses.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "operator"
    phone: Optional[str] = None

class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    created_at: datetime
    phone: Optional[str] = None

class LoginIn(BaseModel):
    username: str
    password: str

class SiloSettings(BaseModel):
    temp_threshold: Optional[float] = None
    co2_threshold: Optional[float] = None
    mq2_threshold: Optional[int] = None
    alert_interval_min: Optional[int] = 5

class SiloCreate(BaseModel):
    name: str
    device_id: str
    location: Optional[Dict[str, float]] = None
    settings: Optional[SiloSettings] = None

class ReadingIn(BaseModel):
    device_id: str
    timestamp: datetime
    temp_C: float
    rh_pct: float
    co2_ppm_est: Optional[float] = None
    mq2_raw: Optional[int] = None
    device_status: Optional[str] = "ok"
    silo_id: Optional[str] = None

class AlertOut(BaseModel):
    id: str
    silo_id: str
    level: str
    message: str
    value: Any
    timestamp: datetime
    acknowledged: bool
