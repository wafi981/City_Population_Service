from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.db.elasticsearch import es_client
from app.settings import settings
from app.models.city import CityUpsert

router = APIRouter(prefix="/cities")


@router.put("/{city_name}")
def upsert_city(city_name: str, payload: CityUpsert):
    doc = {
        "city": city_name.lower(),
        "population": payload.population,
        "updated_at": datetime.utcnow()
    }

    result = es_client.index(
        index=settings.elasticsearch_index,
        id=city_name.lower(),
        document=doc
    )

    return {
        "city": city_name.lower(),
        "population": payload.population,
        "result": result["result"]
    }


@router.get("/{city_name}")
def get_city(city_name: str):
    try:
        res = es_client.get(
            index=settings.elasticsearch_index,
            id=city_name.lower()
        )
    except Exception:
        raise HTTPException(status_code=404, detail="City not found")

    source = res["_source"]
    return {
        "city": source["city"],
        "population": source["population"]
    }
