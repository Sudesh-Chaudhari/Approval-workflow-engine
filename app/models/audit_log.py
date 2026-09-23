from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from app.database import Base
from datetime import datetime, timezone

class Auditlog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.request_id"), nullable=False)
    from_stage_id = Column(Integer, ForeignKey("stages.id"), nullable=True)
    to_stage_id = Column(Integer, ForeignKey("stages.id"), nullable=True)
    action = Column(String, nullable=False)  # "APPROVED", "REJECTED", "KILLED"
    actor = Column(String, nullable=False)  # User who performed the action
    remark = Column(String, nullable=True)  # Optional remark for the action
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))