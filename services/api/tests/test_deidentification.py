from io import BytesIO

from pydicom import Dataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid

from app.main import anonymize_dicom


def test_anonymize_dicom_removes_identity_and_remaps_uids():
    ds = Dataset()
    ds.PatientName = "Test^Patient"
    ds.PatientID = "12345"
    ds.StudyInstanceUID = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SOPInstanceUID = generate_uid()
    ds.FrameOfReferenceUID = generate_uid()
    ds.file_meta = Dataset()
    ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID

    original_study = ds.StudyInstanceUID
    original_series = ds.SeriesInstanceUID
    original_sop = ds.SOPInstanceUID

    anonymize_dicom(ds)

    assert ds.PatientName == ""
    assert ds.PatientID == ""
    assert ds.StudyInstanceUID != original_study
    assert ds.SeriesInstanceUID != original_series
    assert ds.SOPInstanceUID != original_sop
    assert ds.file_meta.MediaStorageSOPInstanceUID == ds.SOPInstanceUID
