# Parking Space Detection - End-to-End DevOps Pipeline by yug shah

A Flask + OpenCV web app that detects free / occupied parking slots from an
image, delivered through a Git -> GitHub Actions -> Docker -> Deploy pipeline.

## Run locally
    pip install -r requirements-dev.txt
    python scripts/make_sample.py sample/parking.png 1,3,4,6
    pytest -v
    python -m app.main            # http://localhost:5000

## Run with Docker
    docker compose up --build -d
    curl http://localhost:5000/health

## API
- `GET  /health`         -> `{"status":"ok"}`
- `POST /api/detect`     -> JSON counts (form field `image`)
- `POST /api/annotate`   -> PNG with green/red boxes

## Pipeline
`.github/workflows/ci-cd.yml` : lint -> test -> docker build & push (GHCR) -> deploy + smoke test.
`Jenkinsfile` : equivalent Jenkins pipeline.
