# OmniSkel-AI

Multimodal musculoskeletal imaging intelligence research platform.

## Phase 1 — Knee MRI vertical slice

DICOM ingestion → preprocessing/QC → anatomy segmentation → pathology inference → quantification → explainability → structured findings → clinical viewer.

> **Research/engineering scaffold.** This repository is not a medical device and must not be used for clinical diagnosis or treatment decisions.

## Repository architecture

```text
omniskel-ai/
├── apps/
│   ├── radiology-dashboard/
│   └── patient-portal/
├── services/
│   ├── dicom-ingestion/
│   ├── inference-api/
│   ├── reporting-service/
│   ├── longitudinal-service/
│   └── audit-service/
├── src/omniskel/
│   ├── core/
│   ├── imaging/
│   ├── inference/
│   ├── models/
│   ├── clinical/
│   ├── longitudinal/
│   ├── explainability/
│   ├── reporting/
│   ├── audit/
│   └── security/
├── models/
├── pipelines/
├── explainability/
├── clinical/
├── evaluation/
├── data/
├── infrastructure/
├── configs/
├── tests/
├── notebooks/
├── docs/
└── scripts/
```

## Quick start

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up --build
```

- Clinical viewer: http://localhost:3000
- API docs: http://localhost:8000/docs
- Model service: http://localhost:8001/docs
- MinIO console: http://localhost:9001

The model service is intentionally a deterministic stub until validated datasets and trained weights are supplied.

## Safety and data policy

Never commit patient-identifiable data, DICOM studies, trained clinical weights, secrets, or production credentials. Use synthetic or properly governed research datasets. De-identification is a research starting point, not a compliance guarantee.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r services/api/requirements.txt
pytest -q
```

See `docs/architecture.md`, `docs/development.md`, and `docs/validation.md`.
