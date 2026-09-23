from __future__ import annotations

import hashlib
import io
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

import boto3
import redis
from botocore.client import Config
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from pydicom import dcmread
from pydicom.dataset import FileDataset
from pydicom.uid import generate_uid
from sqlalchemy import DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

APP_VERSION = "0.2.0"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://omniskel:omniskel@localhost:5432/omniskel")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
OBJECT_STORAGE_ENDPOINT = os.getenv("OBJECT_STORAGE_ENDPOINT", "http://localhost:9000")
OBJECT_STORAGE_BUCKET = os.getenv("OBJECT_STORAGE_BUCKET", "omniskel")
OBJECT_STORAGE_ACCESS_KEY = os.getenv("OBJECT_STORAGE_ACCESS_KEY", "omniskel")
OBJECT_STORAGE_SECRET_KEY = os.getenv("OBJECT_STORAGE_SECRET_KEY", "omniskel-dev-password")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Study(Base):
    __tablename__ = "studies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    study_instance_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    modality: Mapped[str] = mapped_column(String(16))
    anatomy: Mapped[str | None] = mapped_column(String(64), nullable=True)
    study_date: Mapped[str | None] = mapped_column(String(16), nullable=True)
    accession_number: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Series(Base):
    __tablename__ = "series"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    study_id: Mapped[str] = mapped_column(String(64), index=True)
    series_instance_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    series_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    modality: Mapped[str] = mapped_column(String(16))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Instance(Base):
    __tablename__ = "instances"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    study_id: Mapped[str] = mapped_column(String(64), index=True)
    series_id: Mapped[str] = mapped_column(String(64), index=True)
    sop_instance_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    object_key: Mapped[str] = mapped_column(String(512))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PipelineJob(Base):
    __tablename__ = "pipeline_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    study_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="queued")
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Health(BaseModel):
    status: str
    service: str
    version: str


class UploadResponse(BaseModel):
    study_id: str
    series_id: str
    instance_id: str
    sop_instance_uid: str
    object_key: str
    pipeline_job_id: str
    status: str


app = FastAPI(title="OmniSkel-AI API", version=APP_VERSION)


def storage_client():
    return boto3.client(
        "s3",
        endpoint_url=OBJECT_STORAGE_ENDPOINT,
        aws_access_key_id=OBJECT_STORAGE_ACCESS_KEY,
        aws_secret_access_key=OBJECT_STORAGE_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_storage() -> None:
    client = storage_client()
    try:
        client.head_bucket(Bucket=OBJECT_STORAGE_BUCKET)
    except Exception:
        client.create_bucket(Bucket=OBJECT_STORAGE_BUCKET)


def ensure_schema() -> None:
    Base.metadata.create_all(engine)


def anonymize_dicom(ds: FileDataset) -> FileDataset:
    """Basic research de-identification; production deployments need a validated DICOM profile."""
    patient_fields = [
        "PatientName", "PatientID", "PatientBirthDate", "PatientBirthTime",
        "PatientSex", "OtherPatientIDs", "OtherPatientNames", "PatientAddress",
        "PatientTelephoneNumbers", "InstitutionName", "ReferringPhysicianName",
        "PerformingPhysicianName", "OperatorsName", "AccessionNumber",
    ]
    for field in patient_fields:
        if hasattr(ds, field):
            setattr(ds, field, "")

    uid_map: dict[str, str] = {}
    for field in ("StudyInstanceUID", "SeriesInstanceUID", "SOPInstanceUID", "FrameOfReferenceUID"):
        if hasattr(ds, field):
            old = str(getattr(ds, field))
            uid_map.setdefault(old, generate_uid(prefix="1.2.826.0.1.3680043.10.543."))
            setattr(ds, field, uid_map[old])
    if hasattr(ds, "file_meta"):
        if hasattr(ds.file_meta, "MediaStorageSOPInstanceUID"):
            ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID
    return ds


def enqueue_job(job: PipelineJob) -> None:
    r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    payload = json.loads(job.payload)
    r.rpush("omniskel:pipeline", json.dumps(payload))


@app.on_event("startup")
def startup() -> None:
    ensure_schema()
    try:
        ensure_storage()
    except Exception as exc:
        # API remains bootable when MinIO is temporarily unavailable.
        print(f"object storage initialization deferred: {exc}")


@app.get("/health", response_model=Health)
def health():
    return {"status": "ok", "service": "omniskel-api", "version": APP_VERSION}


@app.get("/v1/studies")
def list_studies() -> list[dict[str, Any]]:
    with SessionLocal() as session:
        studies = session.scalars(select(Study).order_by(Study.created_at.desc())).all()
        return [
            {
                "id": s.id,
                "study_instance_uid": s.study_instance_uid,
                "modality": s.modality,
                "anatomy": s.anatomy,
                "study_date": s.study_date,
                "accession_number": s.accession_number,
            }
            for s in studies
        ]


@app.post("/v1/dicom/upload", response_model=UploadResponse)
async def upload_dicom(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith((".dcm", ".dicom")):
        raise HTTPException(status_code=400, detail="Upload a DICOM file (.dcm or .dicom).")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty upload.")
    if len(raw) > 250 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="DICOM instance exceeds 250 MB upload limit.")

    try:
        ds = dcmread(io.BytesIO(raw), force=False)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid DICOM: {exc}") from exc

    required = ("StudyInstanceUID", "SeriesInstanceUID", "SOPInstanceUID", "Modality")
    missing = [field for field in required if not hasattr(ds, field)]
    if missing:
        raise HTTPException(status_code=422, detail={"missing_dicom_tags": missing})

    ds = anonymize_dicom(ds)
    study_uid = str(ds.StudyInstanceUID)
    series_uid = str(ds.SeriesInstanceUID)
    sop_uid = str(ds.SOPInstanceUID)
    modality = str(ds.Modality).upper()
    study_id = "study_" + hashlib.sha1(study_uid.encode()).hexdigest()[:20]
    series_id = "series_" + hashlib.sha1(series_uid.encode()).hexdigest()[:20]
    instance_id = "instance_" + uuid.uuid4().hex[:20]
    object_key = f"dicom/{study_id}/{series_id}/{sop_uid}.dcm"

    out = io.BytesIO()
    ds.save_as(out, write_like_original=False)
    anonymized = out.getvalue()
    digest = hashlib.sha256(anonymized).hexdigest()

    try:
        storage_client().put_object(Bucket=OBJECT_STORAGE_BUCKET, Key=object_key, Body=anonymized, ContentType="application/dicom")
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Object storage unavailable: {exc}") from exc

    with SessionLocal.begin() as session:
        study = session.get(Study, study_id)
        if not study:
            study = Study(
                id=study_id,
                study_instance_uid=study_uid,
                modality=modality,
                anatomy="knee" if modality in {"MR", "MRI", "CR", "DX", "CT"} else None,
                study_date=str(getattr(ds, "StudyDate", "")) or None,
                accession_number=str(getattr(ds, "AccessionNumber", "")) or None,
            )
            session.add(study)

        series = session.scalar(select(Series).where(Series.series_instance_uid == series_uid))
        if not series:
            series = Series(
                id=series_id,
                study_id=study_id,
                series_instance_uid=series_uid,
                series_number=int(ds.SeriesNumber) if hasattr(ds, "SeriesNumber") and str(ds.SeriesNumber).isdigit() else None,
                description=str(getattr(ds, "SeriesDescription", "")) or None,
                modality=modality,
            )
            session.add(series)

        instance = session.scalar(select(Instance).where(Instance.sop_instance_uid == sop_uid))
        if not instance:
            instance = Instance(
                id=instance_id,
                study_id=study_id,
                series_id=series_id,
                sop_instance_uid=sop_uid,
                object_key=object_key,
                sha256=digest,
            )
            session.add(instance)
        else:
            instance_id = instance.id

        job_id = "job_" + uuid.uuid4().hex[:20]
        payload = {
            "job_id": job_id,
            "study_id": study_id,
            "series_id": series_id,
            "trigger": "dicom_upload",
            "modality": modality,
            "anatomy": study.anatomy,
        }
        job = PipelineJob(id=job_id, study_id=study_id, status="queued", payload=json.dumps(payload))
        session.add(job)

    try:
        enqueue_job(job)
    except Exception as exc:
        with SessionLocal.begin() as session:
            persisted = session.get(PipelineJob, job_id)
            if persisted:
                persisted.status = "storage_registered_redis_pending"
        print(f"pipeline enqueue deferred: {exc}")

    return UploadResponse(
        study_id=study_id,
        series_id=series_id,
        instance_id=instance_id,
        sop_instance_uid=sop_uid,
        object_key=object_key,
        pipeline_job_id=job_id,
        status="queued",
    )


@app.post("/v1/pipeline/run")
def run_pipeline(study_id: str, modality: str = "MRI", anatomy: str = "knee"):
    return {
        "study_id": study_id,
        "modality": modality,
        "anatomy": anatomy,
        "status": "queued",
        "message": "Inference orchestration placeholder."
    }
