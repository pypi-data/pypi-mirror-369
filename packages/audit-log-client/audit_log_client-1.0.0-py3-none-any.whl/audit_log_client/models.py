import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class AuditAction(str):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    APPROVE = "APPROVE"
    REJECT = "REJECT"


class AuditTarget(str):
    USER = "USER"
    FILE = "FILE"
    ORDER = "ORDER"
    PRODUCT = "PRODUCT"
    PAYMENT = "PAYMENT"
    CONFIG = "CONFIG"


class AuditLog(BaseModel):
    """审计日志数据模型"""
    action: AuditAction
    target_type: AuditTarget
    target_id: Optional[str] = None
    user_id: str
    description: str
    ip_address: Optional[str] = None
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime.datetime = Field(default_factory=datetime.timezone.utc)