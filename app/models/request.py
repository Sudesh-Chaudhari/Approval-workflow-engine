from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from app.database import Base

class Request(Base):
    __tablename__ = "requests"

    request_id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    current_stage_id = Column(Integer, ForeignKey("stages.id"), nullable=True)
    status = Column(String, nullable=False)  # "PENDING", "APPROVED", "REJECTED", "KILLED"
    submitted_by = Column(String, nullable=False)
    payload = Column(JSON, nullable=True)