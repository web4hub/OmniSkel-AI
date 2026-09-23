# OmniSkel-AI Architecture

DICOM/PACS → ingestion gateway → study orchestrator → modality preprocessing → anatomical foundation model → pathology heads → quantification → longitudinal comparison → explainability → clinical synthesis → viewer / DICOM-SR / FHIR.

## Design rules
1. Keep raw clinical data immutable.
2. Version datasets, preprocessing, models, and output schemas.
3. Never let an LLM directly determine an imaging diagnosis.
4. Preserve pixel/voxel coordinates for every finding.
5. Treat uncertainty as a first-class output.
6. Separate research and clinical environments.
7. Require retrospective and external validation before clinical deployment.
