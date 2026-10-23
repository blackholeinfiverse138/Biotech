"""
Biotech Production API - Enterprise REST Microservice
======================================================
Owner: ANSH (AI/ML + Data Audit Lead)
Task ID: T-GOV-F01 (Remediation & Structural Compliance)
Domain: Biotech Integration, Audit & Convergence

FastAPI production endpoints with strict Pydantic models, role-based authorization,
deterministic evaluation, and complete error boundary protection.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging
import hashlib
import os
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict

from evaluation_engine.rule_engine import BiotechRuleEngine, EvaluationRubric, RuleEvaluationResult
from task_selector.review_orchestrator import (
    BiotechReviewOrchestrator,
    ReviewPacketContract,
    CandidateReviewRecord,
    ReviewStage,
    DecisionState
)
from integrations.local_llm_client import LocalLLMClient, LLMVerificationResponse
from evaluation_engine.pravah_streaming import (
    PravahEventType,
    PravahEvent,
    PravahReplayEngine,
)
from task_selector.state_machine import (
    GovernanceLifecycleState,
    ConcurrencyRecord,
    ConcurrencyGovernanceEngine,
    OCCConflictError,
    InvalidStateTransitionError,
)
from security.middleware import (
    ErrorBoundaryMiddleware,
    UserRole,
    require_role,
    register_used_token
)

logger = logging.getLogger("biotech_production_api")

# =============================================================================
# Inbound / Outbound Strict Pydantic Models
# =============================================================================

class BiotechAuditRequest(BaseModel):
    task_id: str = Field(..., min_length=3, max_length=100, description="Task identifier (e.g. T-GOV-F01)")
    candidate_name: str = Field(..., min_length=2, max_length=50, description="Candidate stream owner (e.g. Sara, Shamit)")
    capability_name: str = Field(..., min_length=3, max_length=100, description="Stream capability name")
    payload: Dict[str, Any] = Field(..., description="Audit observation payload")
    query_drug: Optional[str] = Field(default=None, description="Query drug for attribution testing")
    reported_drugs: Optional[List[str]] = Field(default=None, description="Reported concomitant drug list")
    is_synthetic: bool = Field(default=False, description="Explicit synthetic fixture marker")


class BiotechEvaluationRequest(BaseModel):
    capability: str = Field(..., min_length=2, max_length=50)
    payload: Dict[str, Any] = Field(...)
    query_drug: Optional[str] = None
    reported_drugs: Optional[List[str]] = None


class EntityExtractionRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=10000)
    query_id: Optional[str] = None


class DisagreementRecordRequest(BaseModel):
    review_id: str = Field(..., min_length=5)
    observation: str = Field(..., min_length=5)
    evidence: str = Field(..., min_length=5)
    differing_interpretation: str = Field(..., min_length=5)
    required_verification: str = Field(..., min_length=5)


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    service: str = "Biotech Integration, Audit & Convergence Engine"
    timestamp: str
    active_capabilities: List[str]
    error_boundary_active: bool = True


class MetricsResponse(BaseModel):
    service: str = "Biotech Engine"
    uptime_state: str = "OPERATIONAL"
    deterministic_sha256_verification: str
    active_reviews_count: int
    evaluated_streams_count: int


# =============================================================================
# Core Router & Application Setup
# =============================================================================

class PravahStreamEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    trace_id: str = Field(..., min_length=4, max_length=128, description="Distributed trace ID")
    event_type: PravahEventType = Field(..., description="Canonical Pravah event type")
    payload: Dict[str, Any] = Field(..., description="Event payload data")
    source_system: str = Field(default="BIOTECH", min_length=2, max_length=64, description="Originating system")
    destination: str = Field(default="PRAVAH_REPLAY_LEDGER", min_length=2, max_length=64, description="Target subsystem")


class PravahReplayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    from_sequence: int = Field(default=1, ge=1, description="Start sequence for replay")
    to_sequence: Optional[int] = Field(default=None, ge=1, description="End sequence for replay")


class ConcurrencyTransitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entity_id: str = Field(..., min_length=3, max_length=128, description="Unique entity identifier")
    expected_version: int = Field(..., ge=1, description="Expected OCC record version")
    target_state: GovernanceLifecycleState = Field(..., description="Target DFA lifecycle state")
    actor: str = Field(..., min_length=2, max_length=64, description="Transition operator")
    trace_id: str = Field(..., min_length=4, max_length=128, description="Trace identifier")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Supplementary transition metadata")

router = APIRouter(prefix="/production", tags=["Biotech Production"])

rule_engine = BiotechRuleEngine()
review_orchestrator = BiotechReviewOrchestrator()
llm_client = LocalLLMClient()


@router.get("/health", response_model=HealthResponse)
def get_health():
    """Returns system health and active capability endpoints."""
    return HealthResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        active_capabilities=list(rule_engine.supported_streams.keys())
    )


@router.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    """Returns deterministic runtime state hash proof."""
    canonical_state = {
        "engine_version": rule_engine.version,
        "capabilities": sorted(list(rule_engine.supported_streams.keys()))
    }
    state_hash = rule_engine.compute_state_hash(canonical_state)
    return MetricsResponse(
        deterministic_sha256_verification=state_hash,
        active_reviews_count=len(review_orchestrator.active_reviews),
        evaluated_streams_count=len(rule_engine.supported_streams)
    )


@router.post("/biotech/audit", response_model=EvaluationRubric)
def audit_biotech_payload(
    req: BiotechAuditRequest,
    role: UserRole = Depends(require_role([UserRole.GOVERNOR, UserRole.AUDITOR, UserRole.ANSH_AUDIT_LEAD]))
):
    """
    Primary independent audit endpoint for Ansh:
    Executes full deterministic rule engine checks on inbound payloads.
    """
    logger.info(f"Auditing task [{req.task_id}] for {req.candidate_name} ({req.capability_name})")
    
    # Merge explicit is_synthetic if passed
    payload_to_evaluate = dict(req.payload)
    if req.is_synthetic:
        payload_to_evaluate["is_synthetic"] = True

    rubric = rule_engine.evaluate_full_submission(
        capability=req.capability_name,
        payload=payload_to_evaluate,
        reported_drugs=req.reported_drugs,
        query_drug=req.query_drug
    )
    return rubric


@router.post("/biotech/evaluate", response_model=EvaluationRubric)
def evaluate_submission(
    req: BiotechEvaluationRequest,
    role: UserRole = Depends(require_role([UserRole.GOVERNOR, UserRole.AUDITOR, UserRole.REVIEWER, UserRole.ANSH_AUDIT_LEAD]))
):
    """Evaluates rules across candidate capabilities."""
    return rule_engine.evaluate_full_submission(
        capability=req.capability,
        payload=req.payload,
        reported_drugs=req.reported_drugs,
        query_drug=req.query_drug
    )


@router.post("/biotech/review", response_model=CandidateReviewRecord)
def start_candidate_review_flow(
    packet: ReviewPacketContract,
    role: UserRole = Depends(require_role([UserRole.GOVERNOR, UserRole.AUDITOR, UserRole.ANSH_AUDIT_LEAD]))
):
    """Initiates candidate review workflow across the 9 convergence stages."""
    return review_orchestrator.start_candidate_review(
        candidate_name=packet.candidate_name,
        capability=packet.capability_name,
        packet_contract=packet
    )


@router.post("/biotech/disagreement", response_model=CandidateReviewRecord)
def record_section_16_disagreement(
    req: DisagreementRecordRequest,
    role: UserRole = Depends(require_role([UserRole.GOVERNOR, UserRole.AUDITOR, UserRole.ANSH_AUDIT_LEAD]))
):
    """Records formal Section 16 independent disagreement."""
    return review_orchestrator.record_section_16_disagreement(
        review_id=req.review_id,
        observation=req.observation,
        evidence=req.evidence,
        differing_interpretation=req.differing_interpretation,
        required_verification=req.required_verification
    )


@router.post("/biotech/extract", response_model=LLMVerificationResponse)
def extract_biotech_entities(
    req: EntityExtractionRequest,
    role: UserRole = Depends(require_role([UserRole.GOVERNOR, UserRole.AUDITOR, UserRole.ANSH_AUDIT_LEAD, UserRole.REVIEWER]))
):
    """Extracts entities and adverse events using local LLM with deterministic fallback."""
    return llm_client.verify_biotech_text(text=req.text, query_id=req.query_id)



pravah_engine = PravahReplayEngine(ledger_path="storage/biotech_pravah_replay.jsonl")
concurrency_engine = ConcurrencyGovernanceEngine(pravah_engine=pravah_engine)

@router.post("/api/v1/pravah/stream", response_model=PravahEvent, tags=["Pravah Replay Ledger"])
def stream_pravah_event(
    request: PravahStreamEventRequest,
    role: UserRole = Depends(require_role([UserRole.GOVERNOR, UserRole.AUDITOR, UserRole.REVIEWER, UserRole.ANSH_AUDIT_LEAD, UserRole.CONSUMER]))
) -> PravahEvent:
    """Streams an event to the append-only Pravah replay ledger with cryptographic hash chaining."""
    return pravah_engine.append_event(
        trace_id=request.trace_id,
        event_type=request.event_type,
        payload=request.payload,
        source_system=request.source_system,
        destination=request.destination
    )


@router.post("/api/v1/pravah/replay", response_model=List[PravahEvent], tags=["Pravah Replay Ledger"])
def replay_pravah_events(
    request: PravahReplayRequest,
    role: UserRole = Depends(require_role([UserRole.GOVERNOR, UserRole.AUDITOR, UserRole.REVIEWER, UserRole.ANSH_AUDIT_LEAD, UserRole.CONSUMER]))
) -> List[PravahEvent]:
    """Replays events deterministically from specified sequence range."""
    return pravah_engine.replay(from_sequence=request.from_sequence, to_sequence=request.to_sequence)


@router.get("/api/v1/pravah/integrity", tags=["Pravah Replay Ledger"])
def verify_pravah_integrity() -> Dict[str, Any]:
    """Verifies cryptographic hash continuity and monotonic sequencing of Pravah replay ledger."""
    return pravah_engine.verify_integrity()


@router.post("/api/v1/governance/concurrency/transition", response_model=ConcurrencyRecord, tags=["Concurrency Governance"])
def transition_concurrency_state(
    request: ConcurrencyTransitionRequest,
    role: UserRole = Depends(require_role([UserRole.GOVERNOR, UserRole.AUDITOR, UserRole.ANSH_AUDIT_LEAD]))
) -> ConcurrencyRecord:
    """Executes an Optimistic Concurrency Control (OCC) protected state transition."""
    try:
        return concurrency_engine.transition_state(
            entity_id=request.entity_id,
            expected_version=request.expected_version,
            target_state=request.target_state,
            actor=request.actor,
            trace_id=request.trace_id,
            metadata=request.metadata
        )
    except OCCConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.message)


@router.get("/api/v1/governance/concurrency/state/{entity_id}", tags=["Concurrency Governance"])
def get_concurrency_state(entity_id: str) -> Dict[str, Any]:
    record = concurrency_engine.get_entity_state(entity_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Entity '{entity_id}' not found.")
    return record.model_dump()


@router.post("/api/v1/governance/reset", tags=["System Internal"])
def reset_governance_state(
    role: UserRole = Depends(require_role([UserRole.GOVERNOR, UserRole.ANSH_AUDIT_LEAD]))
) -> Dict[str, str]:
    pravah_engine.reset_for_tests()
    concurrency_engine.reset_for_tests()
    return {"status": "reset_completed"}


# =============================================================================
# FastAPI Application Creation with Error Boundary & Exception Handlers
# =============================================================================

from fastapi.exceptions import RequestValidationError
from starlette.requests import Request


def create_application() -> FastAPI:
    app_instance = FastAPI(
        title="Biotech Integration, Audit & Convergence Microservice",
        description="Production API with strict Pydantic models, error boundary, and deterministic scoring.",
        version="1.0.0"
    )

    @app_instance.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        trace_id = hashlib.sha256(f"{request.url.path}:{os.urandom(8)}".encode()).hexdigest()[:12]
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": exc.status_code,
                "error_type": "HTTPException",
                "message": str(exc.detail),
                "detail": str(exc.detail),
                "trace_id": trace_id
            }
        )

    @app_instance.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        trace_id = hashlib.sha256(f"{request.url.path}:{os.urandom(8)}".encode()).hexdigest()[:12]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "error",
                "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "error_type": "RequestValidationError",
                "message": f"Inbound schema validation error: {str(exc)}",
                "detail": exc.errors(),
                "trace_id": trace_id
            }
        )

    @app_instance.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        trace_id = hashlib.sha256(f"{request.url.path}:{os.urandom(8)}".encode()).hexdigest()[:12]
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "code": status.HTTP_400_BAD_REQUEST,
                "error_type": exc.__class__.__name__,
                "message": f"Malformed request or unhandled boundary failure: {str(exc)}",
                "detail": str(exc),
                "trace_id": trace_id,
                "boundary_action": "fail_closed_safe"
            }
        )

    # Add Error Boundary Middleware (Guarantees ZERO unhandled 500s)
    app_instance.add_middleware(ErrorBoundaryMiddleware)
    app_instance.include_router(router)
    from api.review_routes import router as review_router
    app_instance.include_router(review_router)
    return app_instance


app = create_application()

