from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import health, cities
from app.db.elasticsearch import ensure_index, es_client, wait_for_es


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ----- Startup -----
    try:
        print("Waiting for Elasticsearch...")
        wait_for_es(es_client)
        ensure_index()
        print("Elasticsearch initialized successfully")
    except Exception as e:
        print(f"Elasticsearch initialization failed: {e}")
        raise e  # Fail fast — crash pod so Kubernetes can restart

    yield

    # ----- Shutdown -----
    print("Shutting down application")


app = FastAPI(
    title="City Population Service",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "service": "City Population Service",
        "status": "running",
        "message": "Welcome! Visit /docs for API documentation."
    }


# Include routers
app.include_router(health.router)
app.include_router(cities.router)
