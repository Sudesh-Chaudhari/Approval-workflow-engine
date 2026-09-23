from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class RequestCreate(BaseModel):
    workflow_id: int
    submitted_by: str
    payload: dict[str, Any]


class RequestResponse(BaseModel):
    request_id: int
    workflow_id: int
    current_stage_id: Optional[int]
    status: str
    submitted_by: str
    payload: dict[str, Any]

    class Config:
        from_attributes = True

class RequestAction(BaseModel):
    action: str  # "APPROVE" or "REJECT"
    actor: str
    remarks: Optional[str] = None


class AuditLogResponse(BaseModel):
    log_id: int
    from_stage_id: Optional[int]
    to_stage_id: Optional[int]
    action: str
    actor: str
    remark: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True