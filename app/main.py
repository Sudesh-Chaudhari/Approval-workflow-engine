from fastapi import FastAPI
from app.database import Base, engine

# Import all models so Base knows about every table before create_all runs
from app.models.workflow import Workflow, Stage
from app.models.request import Request
from app.models.audit_log import Auditlog
from app.routers import workflows, requests

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Universal Approval Workflow Engine")


@app.get("/")
def root():
    return {"message": "Workflow engine is running"}

app.include_router(workflows.router)
app.include_router(requests.router)