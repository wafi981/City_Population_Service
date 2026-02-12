# Deployment Guide For City Population Project

This solution deploys:

- City Population Service (FastAPI)
- Elasticsearch (Database)

Both components are packaged inside the provided Helm chart and deployed together on Kubernetes.

## Prerequisites

Ensure the following tools are installed:

- Kubernetes cluster (Minikube, Kind, Docker Desktop, or Cloud K8s)

- kubectl

- Helm v3+


Verify installation:

```
kubectl version --client
helm version
docker version
```


## Deployment Steps


### Option 1: Use Local Helm Charts In the Project:

Navigate Inside helm Folder
```
cd helm/city-population
```

Install Helm Chart:

```
helm install city-population . -n city-pop --create-namespace
```

To Upgrade after a Change:

```
helm upgrade city-population . -n city-pop --create-namespace
```


### Option 2: Install Directly From Hosted Helm Repository:

```
helm repo add city-pop https://wafi981.github.io/helm-chart
helm repo update
```

Install the Chart:

```
helm install city-population city-pop/city-population -n city-pop --create-namespace
```


## Verify Deployment

Check the pods:

```
 kubectl get pods -n city-pop
```


Expected Output:

```
NAME                                       READY   STATUS    RESTARTS   AGE
city-population-service-676b98cb89-9ln7b   1/1     Running   0          3h11m
elasticsearch-65cd8db49-xl8gz              1/1     Running   0          3h11m

```

### Note:
Rolling updates, resource governance, and zero-downtime deployments are enforced via Kubernetes Deployment strategy (RollingUpdate with maxUnavailable: 0), explicit CPU/memory requests & limits, and dedicated startup, readiness, and liveness probes (see Helm templates).

## Access the Application:

We have deployed these applications and exposed Via ClusterIP Service, to access them we need to use port-forwarding:

For Application:

```
kubectl port-forward svc/city-population-service  8000:80 -n city-pop
```

For Database:
```
 kubectl port-forward svc/elasticsearch 9200:9200 -n city-pop
```

Please ensure that these commands are running in the background or in seperate terminals before we start testing.


## API Endpoints Verifications 

### Health Check
```
curl http://localhost:8000/health
```

Response:

```
{"status":"ok"}
```

### Liveliness Check
```
curl http://localhost:8000/health/live
```

Response:

```
{"status":"alive"}
```


### Readiness Check
```
curl http://localhost:8000/health/ready
```

Response:

```
{"status":"ready"}
```

### Insert or Update a City (Upsert)


```
curl -X PUT http://localhost:8000/cities/Tokyo \
  -H "Content-Type: application/json" \
  -d '{
    "population": 13960000
  }'

```

Response:

```
{"city":"tokyo","population":13960000,"result":"created"}
```

### Query a City
```
curl http://localhost:8000/cities/Tokyo
```

Response: 
```
{"city":"tokyo","population":13960000}
```

### Updated the City population
```
curl -X PUT http://localhost:8000/cities/Tokyo \
  -H "Content-Type: application/json" \
  -d '{
    "population": 6000000 
  }'
```

Response:
```
{"city":"tokyo","population":6000000,"result":"updated"}
```

## API Documentation (Swagger UI)

FastAPI automatically generates interactive documentation.

Open in browser:
```
http://localhost:8000/docs
```

You can test all endpoints directly from the UI.


## Verify Data in Elasticsearch

Check indices:
```
curl "http://localhost:9200/_cat/indices?v"
```

Response:
```
health status index            uuid                   pri rep docs.count docs.deleted store.size pri.store.size dataset.size
yellow open   city-populations q3cDEOYdSJeZ_rx8wAmSxA   1   1          1            0      4.7kb          4.7kb        4.7kb

```


Search data:
```
curl "http://localhost:9200/city-populations/_search?pretty"
```
Response:

```
{
  "took" : 92,
  "timed_out" : false,
  "_shards" : {
    "total" : 1,
    "successful" : 1,
    "skipped" : 0,
    "failed" : 0
  },
  "hits" : {
    "total" : {
      "value" : 1,
      "relation" : "eq"
    },
    "max_score" : 1.0,
    "hits" : [
      {
        "_index" : "city-populations",
        "_id" : "tokyo",
        "_score" : 1.0,
        "_source" : {
          "city" : "tokyo",
          "population" : 6000000,
          "updated_at" : "2026-02-12T10:11:36.651994"
        }
      }
    ]
  }
}
```



**NOTE**
For URLs with query parameters, always quote them in zsh, PowerShell, or cmd:

```
curl "http://localhost:9200/city-populations/_search?pretty"
```

## Uninstall the application
```
helm uninstall city-population -n city-pop
```

## Other Deployment Scenarios:

If you want to deploy the app on your local system please go to the docs folder where we have 2 more implementations:

1.) Application Running in a non-containerised form

2.) Application Running on local system as docker container

## Challaenges & Production Suggestions

Please Navigate to [Reflection.md](Reflection.md) file to have a look at the challenges faced during deployments & suggestions for production deployment.

## Project Structure:

- app:        Folder with all the Python files used in implementation of the app.
- docs:       Folder with Tutorials showing other ways of deploying our application 
- helm:       Folder with our kubernetes configuration or helm chart files


## Build the docker image (multi-platform):

If you do not want to use the pre-built docker image and build it yourself to please run:

```
docker buildx create --use --name multiarch || true
docker buildx inspect --bootstrap

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t <your-dockerhub-username>/city-population-service:<tag> \
  --push .
```

## Troubleshooting Tips:

1.) FastAPI not reachable: check port-forwarding, container port matches service targetPort.

2.) Elasticsearch not ready: check logs (kubectl logs) and wait_for_es retries.
