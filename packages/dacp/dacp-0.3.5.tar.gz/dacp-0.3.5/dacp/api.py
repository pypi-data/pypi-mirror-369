#!/usr/bin/env python3
"""
DACP REST API Server

Provides HTTP endpoints for running workflows and managing agents.
"""

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

import dacp
from dacp.workflow_runtime import WorkflowRuntime


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dacp.api")


# Pydantic models for API requests/responses
class WorkflowExecuteRequest(BaseModel):
    workflow_file: str = Field(..., description="Path to workflow YAML file")
    workflow_name: str = Field(..., description="Name of workflow to execute")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for workflow")
    session_id: Optional[str] = Field(None, description="Custom session ID")
    wait_for_completion: bool = Field(
        True, description="Wait for workflow completion or return immediately"
    )


class WorkflowStatusResponse(BaseModel):
    workflow_id: str
    status: str
    created_at: float
    started_at: Optional[float]
    completed_at: Optional[float]
    duration: Optional[float]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    steps: Optional[Dict[str, Any]]


class WorkflowListResponse(BaseModel):
    workflows: Dict[str, Dict[str, Any]]
    agents: list


class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float
    active_workflows: int


# Global state
app = FastAPI(
    title="DACP REST API",
    description="REST API for Declarative Agent Communication Protocol",
    version="0.3.3",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global runtime and session tracking
runtime: Optional[WorkflowRuntime] = None
orchestrator: Optional[dacp.Orchestrator] = None
start_time = time.time()
active_workflows: Dict[str, Dict[str, Any]] = {}


def get_runtime() -> WorkflowRuntime:
    """Get or create the global workflow runtime."""
    global runtime, orchestrator

    if runtime is None:
        orchestrator = dacp.Orchestrator(session_id=f"api-{int(time.time())}")
        runtime = dacp.WorkflowRuntime(orchestrator=orchestrator)
        logger.info("🚀 DACP API runtime initialized")

    return runtime


@app.on_event("startup")
async def startup_event():
    """Initialize the API on startup."""
    get_runtime()
    logger.info("🎭 DACP REST API server started")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "DACP REST API",
        "version": "0.3.2",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global active_workflows

    return HealthResponse(
        status="healthy",
        version="0.3.3",
        uptime=time.time() - start_time,
        active_workflows=len(active_workflows),
    )


@app.post("/workflows/execute", response_model=WorkflowStatusResponse)
async def execute_workflow(request: WorkflowExecuteRequest, background_tasks: BackgroundTasks):
    """Execute a workflow."""
    try:
        runtime = get_runtime()

        # Validate workflow file exists
        workflow_path = Path(request.workflow_file)
        if not workflow_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Workflow file not found: {request.workflow_file}",
            )

        # Load workflow configuration
        runtime.load_workflow_config(str(workflow_path))

        # Generate workflow ID
        workflow_id = str(uuid.uuid4())

        # Create initial status
        status = WorkflowStatusResponse(
            workflow_id=workflow_id,
            status="pending",
            created_at=time.time(),
            started_at=None,
            completed_at=None,
            duration=None,
            result=None,
            error=None,
            steps=None,
        )

        # Track active workflow
        active_workflows[workflow_id] = {
            "status": status,
            "request": request,
            "created_at": time.time(),
        }

        if request.wait_for_completion:
            # Execute synchronously
            try:
                status.started_at = time.time()
                status.status = "running"

                # Execute workflow
                actual_workflow_id = runtime.execute_workflow(
                    request.workflow_name, request.input_data
                )

                # Get results
                workflow_status = runtime.get_workflow_status(actual_workflow_id)

                status.completed_at = time.time()
                if status.started_at is not None:
                    status.duration = status.completed_at - status.started_at
                status.status = "completed"
                status.result = workflow_status

                # Clean up
                active_workflows.pop(workflow_id, None)

                logger.info(f"✅ Workflow {workflow_id} completed in {status.duration:.2f}s")

            except Exception as e:
                status.completed_at = time.time()
                if status.started_at is not None:
                    status.duration = status.completed_at - status.started_at
                status.status = "failed"
                status.error = str(e)

                # Clean up
                active_workflows.pop(workflow_id, None)

                logger.error(f"❌ Workflow {workflow_id} failed: {e}")

        else:
            # Execute asynchronously
            background_tasks.add_task(execute_workflow_async, workflow_id, request, runtime)
            logger.info(f"🚀 Workflow {workflow_id} queued for async execution")

        return status

    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def execute_workflow_async(
    workflow_id: str, request: WorkflowExecuteRequest, runtime: WorkflowRuntime
):
    """Execute a workflow asynchronously."""
    try:
        # Update status to running
        if workflow_id in active_workflows:
            active_workflows[workflow_id]["status"].started_at = time.time()
            active_workflows[workflow_id]["status"].status = "running"

        # Execute workflow
        actual_workflow_id = runtime.execute_workflow(request.workflow_name, request.input_data)

        # Get results
        workflow_status = runtime.get_workflow_status(actual_workflow_id)

        # Update status
        if workflow_id in active_workflows:
            status = active_workflows[workflow_id]["status"]
            status.completed_at = time.time()
            if status.started_at is not None:
                status.duration = status.completed_at - status.started_at
            status.status = "completed"
            status.result = workflow_status

            # Clean up
            del active_workflows[workflow_id]

        logger.info(f"✅ Async workflow {workflow_id} completed")

    except Exception as e:
        # Update status with error
        if workflow_id in active_workflows:
            status = active_workflows[workflow_id]["status"]
            status.completed_at = time.time()
            if status.started_at is not None:
                status.duration = status.completed_at - status.started_at
            status.status = "failed"
            status.error = str(e)

            # Clean up
            del active_workflows[workflow_id]

        logger.error(f"❌ Async workflow {workflow_id} failed: {e}")


@app.get("/workflows/{workflow_id}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflow_id: str):
    """Get the status of a workflow execution."""
    if workflow_id in active_workflows:
        return active_workflows[workflow_id]["status"]
    else:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")


@app.get("/workflows", response_model=Dict[str, Any])
async def list_active_workflows():
    """List all active workflows."""
    return {
        "active_workflows": len(active_workflows),
        "workflows": [
            {
                "workflow_id": wf_id,
                "status": wf_data["status"].status,
                "created_at": wf_data["created_at"],
                "workflow_name": wf_data["request"].workflow_name,
            }
            for wf_id, wf_data in active_workflows.items()
        ],
    }


@app.get("/workflows/config/{workflow_file}", response_model=WorkflowListResponse)
async def get_workflow_config(workflow_file: str):
    """Get workflow configuration and list available workflows."""
    try:
        workflow_path = Path(workflow_file)
        if not workflow_path.exists():
            raise HTTPException(status_code=404, detail=f"Workflow file not found: {workflow_file}")

        # Load workflow configuration
        import yaml

        with open(workflow_path, "r") as f:
            config = yaml.safe_load(f)

        return WorkflowListResponse(
            workflows=config.get("workflows", {}), agents=config.get("agents", [])
        )

    except Exception as e:
        logger.error(f"❌ Failed to load workflow config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/workflows/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """Cancel a running workflow."""
    if workflow_id not in active_workflows:
        raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

    # Update status to cancelled
    active_workflows[workflow_id]["status"].status = "cancelled"
    active_workflows[workflow_id]["status"].completed_at = time.time()

    # Clean up
    del active_workflows[workflow_id]

    logger.info(f"🚫 Workflow {workflow_id} cancelled")
    return {"message": f"Workflow {workflow_id} cancelled"}


@app.get("/agents", response_model=Dict[str, Any])
async def list_agents():
    """List registered agents."""
    runtime = get_runtime()
    agents = runtime.agent_registry.list_agents()

    agent_info = []
    for agent_id in agents:
        info = runtime.agent_registry.get_agent_info(agent_id)
        if info:
            agent_info.append(info)

    return {"agents": agent_info, "total": len(agents)}


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the DACP API server."""
    logger.info(f"🚀 Starting DACP REST API server on {host}:{port}")

    uvicorn.run("dacp.api:app", host=host, port=port, reload=reload, log_level="info")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DACP REST API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()
    start_server(args.host, args.port, args.reload)
