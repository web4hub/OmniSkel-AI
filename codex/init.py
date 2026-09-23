from pathlib import Path
import textwrap, json, zipfile, shutil

root = Path("/mnt/data/OmniSkel-AI")
if root.exists():
    shutil.rmtree(root)
root.mkdir(parents=True)

files = {}

def add(path, content=""):
    files[path] = textwrap.dedent(content).lstrip("\n")

# Root / governance
add(".gitignore", r"""
.env
.env.*
!.env.example
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.next/
node_modules/
dist/
build/
coverage/
.venv/
venv/
.DS_Store
*.log
*.sqlite
data/raw/*
data/processed/*
data/annotations/*
data/manifests/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/annotations/.gitkeep
!data/manifests/.gitkeep
models/*/weights/*
!models/*/weights/.gitkeep
""")

add(".env.example", r"""
POSTGRES_USER=omniskel
POSTGRES_PASSWORD=omniskel
POSTGRES_DB=omniskel
DATABASE_URL=postgresql://omniskel:omniskel@localhost:5432/omniskel
REDIS_URL=redis://localhost:6379/0
OBJECT_STORAGE_ENDPOINT=http://localhost:9000
OBJECT_STORAGE_BUCKET=omniskel
OBJECT_STORAGE_ACCESS_KEY=omniskel
OBJECT_STORAGE_SECRET_KEY=omniskel-dev-password
MODEL_SERVICE_URL=http://localhost:8001
API_PORT=8000
VIEWER_PORT=3000
OMNISKEL_ENV=research
""")

add("LICENSE", """
MIT License

Copyright (c) 2026 OmniSkel-AI contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files, to deal in the Software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the
Software, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
""")

add("README.md", """
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
