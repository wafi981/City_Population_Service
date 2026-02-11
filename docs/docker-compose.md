# Docker Compose Deployment Guide

This guide explains how to run the City Population Service together with Elasticsearch using Docker Compose.

This method is intended for:
- Local development
- Quick testing
- Non-Kubernetes environments

---

## Prerequisites

- Docker (v20+ recommended)
- Docker Compose (v2+)

Verify installation:

```
docker --version
docker compose version
```

## Start the Application

From the project root:

```
docker-compose up -d
```

This will:

Start Elasticsearch

Start the City Population Service

Automatically connect the application to Elasticsearch


## Testing
To test the applications please follow the steps given in local.md or the main README at the project root.

## Stop the Environment
```
docker-compose down
```

To remove volumes (delete Elasticsearch data):
```
docker compose down -v
```