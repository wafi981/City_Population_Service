import time
import logging
from elasticsearch import Elasticsearch
from app.settings import settings

logger = logging.getLogger(__name__)

es_client = Elasticsearch(settings.elasticsearch_host)

def wait_for_es(es: Elasticsearch, retries: int = 30, delay: int = 2):
    logger.info("Waiting for Elasticsearch to become available...")
    for i in range(retries):
        try:
            if es.ping():
                logger.info("Elasticsearch is available")
                return
        except Exception:
            logger.warning("Elasticsearch not ready yet (%d/%d)", i + 1, retries)

        time.sleep(delay)

    raise RuntimeError("Elasticsearch not available after retries")


def ensure_index():
    logger.info("Using Elasticsearch index: %s", settings.elasticsearch_index)

    if not es_client.indices.exists(index=settings.elasticsearch_index):
        es_client.indices.create(
            index=settings.elasticsearch_index,
            mappings={
                "properties": {
                    "city": {"type": "keyword"},
                    "population": {"type": "long"},
                    "updated_at": {"type": "date"}
                }
            }
        )
