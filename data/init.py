from pathlib import Path
import zipfile, textwrap, json, shutil

root = Path("/mnt/data/OmniSkel-AI-generated")
if root.exists():
    shutil.rmtree(root)
root.mkdir(parents=True)

files = {
"README.md": """# OmniSkel-AI

Multimodal musculoskeletal imaging intelligence research platform.

## Phase 1 — Knee MRI vertical slice

DICOM ingestion → preprocessing/QC → anatomy segmentation → pathology inference → quantification → explainability → structured findings → clinical viewer.

> Research/engineering scaffold. Not a medical device and not for clinical diagnosis.

## Repository layout

- `apps/` — user-facing applications
- `services/` — backend services
- `models/` — model packages and model metadata
- `pipelines/` — preprocessing, datasets, augmentation, evaluation and orchestration
- `clinical/` — DICOM/FHIR/terminology/reporting boundaries
- `explainability/` — Grad-CAM, SHAP and attribution interfaces
- `infrastructure/` — Docker, Kubernetes, monitoring and security
- `data/` — manifests/schemas only; never commit patient data
- `evaluation/` — benchmarks, metrics, calibration, robustness and validation
- `src/omniskel/` — shared Python domain modules
- `tests/` — unit/integration/contract tests

## Local development

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up --build
