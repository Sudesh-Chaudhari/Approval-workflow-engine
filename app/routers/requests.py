from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.workflow import Workflow, Stage
from app.models.request import Request
from app.schemas.request import AuditLogResponse, RequestCreate, RequestResponse, RequestAction
from app.models.audit_log import Auditlog

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post("/", response_model=RequestResponse)
def create_request(payload: RequestCreate, db: Session = Depends(get_db)):
    # Step 1: Check the workflow actually exists
    workflow = db.query(Workflow).filter(Workflow.id == payload.workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Step 2: Find the first stage (sequence_order == 1) for this workflow
    first_stage = (
        db.query(Stage)
        .filter(Stage.workflow_id == payload.workflow_id, Stage.sequence_order == 1)
        .first()
    )
    if not first_stage:
        raise HTTPException(status_code=400, detail="Workflow has no starting stage")

    # Step 3: Create the request, starting at that first stage
    new_request = Request(
        workflow_id=payload.workflow_id,
        current_stage_id=first_stage.id,
        status="PENDING",
        submitted_by=payload.submitted_by,
        payload=payload.payload,
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return new_request

@router.post("/{request_id}/action", response_model=RequestResponse)
def process_action(request_id: int, payload: RequestAction, db: Session = Depends(get_db)):
    # Step 1: Fetch the request
    req = db.query(Request).filter(Request.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if req.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Request already {req.status}, no action allowed")

    # Step 2: Fetch its current stage
    current_stage = db.query(Stage).filter(Stage.id == req.current_stage_id).first()

    from_stage_id = current_stage.id
    to_stage_id = None

    # Step 3: Apply the action
    if payload.action == "APPROVE":
        if current_stage.on_approve_next_stage_id is None:
            req.status = "APPROVED"
            req.current_stage_id = None
        else:
            req.current_stage_id = current_stage.on_approve_next_stage_id
            to_stage_id = req.current_stage_id

    elif payload.action == "REJECT":
        if current_stage.on_reject_action == "KILL":
            req.status = "REJECTED"
            req.current_stage_id = None
        elif current_stage.on_reject_action == "GO_TO_STAGE":
            req.current_stage_id = current_stage.on_reject_target_stage_id
            to_stage_id = req.current_stage_id
    else:
        raise HTTPException(status_code=400, detail="action must be APPROVE or REJECT")

    # Step 4: Write the audit log — happens regardless of outcome
    log = Auditlog(
        request_id=req.request_id,
        from_stage_id=from_stage_id,
        to_stage_id=to_stage_id,
        action=payload.action,
        actor=payload.actor,
        remark=payload.remarks,
    )
    db.add(log)

    db.commit()
    db.refresh(req)

    return req

@router.get("/{request_id}/audit-log", response_model=list[AuditLogResponse])
def get_audit_log(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    audit_logs = (
        db.query(Auditlog)
        .filter(Auditlog.request_id == request_id)
        .order_by(Auditlog.timestamp.asc())
        .all()
    )

    return audit_logs

@router.get("/", response_model=list[RequestResponse])
def list_requests(db: Session = Depends(get_db)):
    return db.query(Request).all()

@router.get("/{request_id}", response_model=RequestResponse)
def get_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.request_id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req