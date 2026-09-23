from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.workflow import Workflow, Stage
from app.schemas.workflow import WorkflowCreate, WorkflowResponse
from app.services.workflow_engine import has_reject_cycle

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post("/", response_model=WorkflowResponse)
def create_workflow(payload: WorkflowCreate, db: Session = Depends(get_db)):
    if has_reject_cycle(payload.stages):
        raise HTTPException(status_code=400, detail="Invalid workflow: reject routing forms a cycle")

    # Step 1: Create the Workflow row
    new_workflow = Workflow(name=payload.name)
    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)

    # Step 2: Sort incoming stages by sequence_order (don't trust JSON array order)
    sorted_stages = sorted(payload.stages, key=lambda s: s.sequence_order)

    # Step 3: Insert all stages first, WITHOUT linking (IDs don't exist yet)
    created_stages = []
    for stage_data in sorted_stages:
        new_stage = Stage(
            workflow_id=new_workflow.id,
            stage_name=stage_data.stage_name,
            sequence_order=stage_data.sequence_order,
            approver_role=stage_data.approver_role,
            on_reject_action=stage_data.on_reject_action,
        )
        db.add(new_stage)
        created_stages.append(new_stage)

    db.commit()
    for stage in created_stages:
        db.refresh(stage)

    # Step 4: NOW go back and link — all IDs exist at this point
    for i, stage in enumerate(created_stages):
        if i + 1 < len(created_stages):
            stage.on_approve_next_stage_id = created_stages[i + 1].id
        else:
            stage.on_approve_next_stage_id = None

        reject_seq = sorted_stages[i].on_reject_target_sequence
        if reject_seq is not None:
            target = next((s for s in created_stages if s.sequence_order == reject_seq), None)
            stage.on_reject_target_stage_id = target.id if target else None

    db.commit()
    db.refresh(new_workflow)

    return new_workflow


@router.get("/", response_model=list[WorkflowResponse])
def list_workflows(db: Session = Depends(get_db)):
    return db.query(Workflow).all()


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow