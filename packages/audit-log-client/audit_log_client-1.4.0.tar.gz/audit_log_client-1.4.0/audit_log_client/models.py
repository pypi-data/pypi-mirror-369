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
    """审计日志数据模型 - 开放扩展字段"""
    # 核心字段
    action: AuditAction
    target_type: AuditTarget
    user_id: str
    description: str
    
    # 可选核心字段
    target_id: Optional[str] = None
    ip_address: Optional[str] = None
    before: Optional[Dict[str, Any]] = None
    after: Optional[Dict[str, Any]] = None
    
    # 时间戳
    timestamp: datetime.datetime = Field(default_factory=datetime.timezone.utc)
    
    # 扩展字段 - 允许任意额外字段
    class Config:
        extra = "allow"