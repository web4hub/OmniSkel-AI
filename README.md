# OmniSkel-AI

Multimodal musculoskeletal imaging intelligence platform.

## Phase 1 MVP
Knee MRI vertical slice:
DICOM ingestion → preprocessing/QC → anatomy segmentation → pathology inference → quantification → explainability → structured findings → clinical viewer.

> Research/engineering scaffold. Not a medical device and not for clinical diagnosis.

## Quick start

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up --build
```

UI: http://localhost:3000
API docs: http://localhost:8000/docs
Model service: http://localhost:8001/docs

The model service is intentionally a stub until validated datasets and trained weights are supplied.

## M1 DICOM ingestion

The API now exposes `POST /v1/dicom/upload` for individual DICOM instances. The ingestion path parses and validates the DICOM, applies the research de-identification routine, remaps UIDs, stores the anonymized object in MinIO, registers Study/Series/Instance records in Postgres, and queues a pipeline job in Redis. This is a research scaffold and the de-identification profile must be validated and hardened before any clinical deployment.

Example:

```bash
curl -F "file=@/path/to/instance.dcm" http://localhost:8000/v1/dicom/upload
```
