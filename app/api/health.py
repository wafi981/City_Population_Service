from fastapi import APIRouter, HTTPException
from app.db.elasticsearch import es_client

router = APIRouter(tags=["Health"])

@router.get("/health")
def health():
    """
    Assignment-required health endpoint.
    Returns OK.
    """
    return {"status": "ok"}


@router.get("/health/live")
def liveness():
    """
    Kubernetes liveness probe.
    """
    return {"status": "alive"}


@router.get("/health/ready")
def readiness():
    """
    Kubernetes readiness probe.
    """
    try:
        if not es_client.ping():
            raise HTTPException(status_code=503, detail="Elasticsearch not ready")
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Elasticsearch not reachable")
