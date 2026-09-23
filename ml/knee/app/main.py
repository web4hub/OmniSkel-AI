from typing import Literal
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="OmniSkel Knee Model Service", version="0.1.0")

class InferenceRequest(BaseModel):
    study_id: str
    modality: Literal["MRI", "XR", "CT"] = "MRI"
    anatomy: str = "knee"

@app.get("/health")
def health():
    return {"status": "ok", "service": "knee-model-service"}

@app.post("/v1/infer")
def infer(req: InferenceRequest):
    return {
        "study_id": req.study_id,
        "model_version": "knee-mvp-stub-0.1.0",
        "status": "stub",
        "findings": [],
        "measurements": [],
        "segments": [],
        "uncertainty": None,
    }
