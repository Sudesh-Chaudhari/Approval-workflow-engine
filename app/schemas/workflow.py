from pydantic import BaseModel
from typing import Optional

class StageCreate(BaseModel):
    stage_name: str
    sequence_order: int
    approver_role: str
    on_reject_action: str
    on_reject_target_sequence: Optional[int] = None


class WorkflowCreate(BaseModel):
    name: str
    stages: list[StageCreate]


class StageResponse(BaseModel):
    id: int
    stage_name: str
    sequence_order: int
    approver_role: str
    on_approve_next_stage_id: Optional[int]
    on_reject_action: str
    on_reject_target_stage_id: Optional[int]

    class Config:
        from_attributes = True


class WorkflowResponse(BaseModel):
    id: int
    name: str
    stages: list[StageResponse]

    class Config:
        from_attributes = True