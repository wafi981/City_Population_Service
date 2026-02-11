from fastapi import FastAPI
from app.api import health, cities
from app.db.elasticsearch import ensure_index, es_client, wait_for_es
import threading


app = FastAPI(title="City Population Service")

def init_elasticsearch():
    try:
        wait_for_es(es_client)
        ensure_index()
        print("Elasticsearch initialized successfully")
    except Exception as e:
        print(f"Elasticsearch initialization failed: {e}")

@app.on_event("startup")
def startup():
    thread = threading.Thread(target=init_elasticsearch, daemon=True)
    thread.start()

app.include_router(health.router)
app.include_router(cities.router)
