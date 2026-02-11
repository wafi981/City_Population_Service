# City Population Service — Local Deployment Guide (No Docker / No Kubernetes)

This guide explains how to run the application end-to-end on a local machine with elastic container deployed using docker.
It includes:

- Installing and running Elasticsearch on docker

- Installing Python dependencies

- Running the FastAPI application

- Testing the API endpoints


## 1. Prerequisites

Make sure the following are installed:

- Python 3.11+

- pip

- curl (optional, for testing)

- Elasticsearch 8.x


Check Python:

```
python --version
```


## 2. Start Elasticsearch in Docker

Run:
```
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.13.4
```

Verify Elasticsearch is Running

```
curl http://localhost:9200
```

You should see JSON cluster info like:
```
{
  "cluster_name": "docker-cluster",
  "version": {
    "number": "8.13.4"
  }
}
```

## 3. Create Virtual Environment
```
python -m venv venv
source venv/bin/activate     # macOS/Linux
# or
venv\Scripts\activate        # Windows
```

## 5. Install Dependencies

```
pip install -r requirements.txt
```

## 6. Configure Environment Variables

Create a .env file in the project root:

```
ELASTICSEARCH_HOST=http://localhost:9200
ELASTICSEARCH_INDEX=city-populations
```

Or export manually:
```
export ELASTICSEARCH_HOST=http://localhost:9200
export ELASTICSEARCH_INDEX=city-populations
```


## 7. Run the Application

Start the FastAPI app using Uvicorn:

```
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:

```
Application startup complete.
Uvicorn running on http://0.0.0.0:8000
```


The application will:

- Wait for Elasticsearch

- Create the index if it does not exist

- Start serving API requests

## 8. Test the API
Health Check
```
curl http://localhost:8000/health
```

Response:

```
{"status":"ok"}
```

Insert or Update a City (Upsert)
```
curl -X PUT http://localhost:8000/cities/Tokyo \
  -H "Content-Type: application/json" \
  -d '{
    "population": 13960000
  }'

```

Query a City
```
curl http://localhost:8000/cities/Tokyo
```

Response:
```
{
  "city": "Tokyo",
  "population": 13960000
}
```

## 9. API Documentation (Swagger UI)

FastAPI automatically generates interactive documentation.

Open in browser:
```
http://localhost:8000/docs
```

You can test all endpoints directly from the UI.

## 10. Verify Data in Elasticsearch

Check indices:
```
curl http://localhost:9200/_cat/indices?v
```

Search data:
```
curl http://localhost:9200/city-populations/_search?pretty
```


## 11. Stopping the Application

Stop FastAPI:

```
CTRL + C
```

Stop Elasticsearch:
```
CTRL + C
```

or
```
brew services stop elasticsearch
```

## Architecture (Local Mode)
```
User → FastAPI (Port 8000) → Elasticsearch (Port 9200)
```

