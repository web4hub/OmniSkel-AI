# Development Roadmap

## M0 — Scaffold
- repository structure
- API/model-service boundaries
- local Postgres, Redis and MinIO
- shared finding contract
- research-mode viewer

## M1 — DICOM ingestion
- multipart DICOM upload endpoint
- strict DICOM parsing and required-tag validation
- basic research de-identification with UID remapping
- Study / Series / Instance registration in Postgres
- anonymized DICOM object storage in MinIO/S3-compatible storage
- Redis pipeline job creation
- duplicate SOP-instance handling
- upload-size and invalid-file guards

> The de-identification routine is intentionally a starting point, not a production HIPAA/GDPR or local-regulatory compliance implementation. A validated DICOM confidentiality profile and site-specific policy must replace/extend it before clinical use.

## M2 — Knee MRI inference
- sequence classifier
- image quality control
- anatomy segmentation
- ACL/PCL/meniscus/cartilage heads
- measurement engine

## M3 — Clinical workbench
- DICOM viewer
- overlays
- findings panel
- longitudinal comparison
- structured report

## M4 — Validation
- patient-level train/validation/test splits
- external validation
- calibration
- subgroup analysis
- robustness testing
- prospective workflow validation
