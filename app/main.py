from fastapi import FastAPI
from app.api import health, cities
from app.db.elasticsearch import ensure_index, es_client, wait_for_es

app = FastAPI(title="City Population Service")

@app.on_event("startup")
def startup():
    wait_for_es(es_client)
    ensure_index()

app.include_router(health.router)
app.include_router(cities.router)
