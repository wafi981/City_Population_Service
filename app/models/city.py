from pydantic import BaseModel, Field


class CityUpsert(BaseModel):
    population: int = Field(..., gt=0)


class CityResponse(BaseModel):
    city: str
    population: int
