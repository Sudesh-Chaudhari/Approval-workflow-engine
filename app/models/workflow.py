from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    stages = relationship("Stage", back_populates="workflow", order_by="Stage.sequence_order")


class Stage(Base):
    __tablename__ = "stages"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    stage_name = Column(String, nullable=False)
    sequence_order = Column(Integer, nullable=False)
    approver_role = Column(String, nullable=False)
    on_approve_next_stage_id = Column(Integer, ForeignKey("stages.id"), nullable=True)
    on_reject_action = Column(String, nullable=False)  # "KILL" or "GO_TO_STAGE"
    on_reject_target_stage_id = Column(Integer, ForeignKey("stages.id"), nullable=True)

    workflow = relationship("Workflow", back_populates="stages", foreign_keys=[workflow_id])