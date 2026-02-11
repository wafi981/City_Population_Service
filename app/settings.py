from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    elasticsearch_host: str = "http://localhost:9200"
    elasticsearch_index: str = "city-populations"


settings = Settings()
