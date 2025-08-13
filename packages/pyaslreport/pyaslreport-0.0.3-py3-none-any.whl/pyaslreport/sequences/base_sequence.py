import os
import pydicom
from abc import ABC, abstractmethod
from pyaslreport.io.writers import JSONWriter, TsvWriter
from pyaslreport.converters import DICOM2NiFTIConverter
from pyaslreport.utils import dicom_tags_utils as dcm_tags
from pyaslreport.utils import UnitConverterUtils

class BaseSequence(ABC):
    def __init__(self, dicom_header: pydicom.Dataset):
        self.dicom_header = dicom_header

    @classmethod
    @abstractmethod
    def matches(cls, dicom_header: pydicom.Dataset) -> bool:
        """Return True if this class can handle the given DICOM header."""
        pass

    @classmethod
    def get_specificity_score(cls) -> int:
        """
        Return a specificity score for this sequence class.
        Higher scores indicate more specific matching criteria.
        Override in subclasses to provide custom specificity.
        """
        return 0

    @abstractmethod
    def extract_bids_metadata(self) -> dict:
        """Extract and convert DICOM metadata to BIDS fields."""
        pass

    def _extract_common_metadata(self) -> dict:
        """Extract and convert common DICOM metadata fields to BIDS fields, including ms->s conversion where needed."""
        dataset = self.dicom_header
        
        bids = {}

        # Direct mappings
        for dicom_key, bids_key in [
            (dcm_tags.MANUFACTURER, "Manufacturer"),
            (dcm_tags.MANUFACTURERS_MODEL_NAME, "ManufacturersModelName"),
            (dcm_tags.SOFTWARE_VERSIONS, "SoftwareVersions"),
            (dcm_tags.MAGNETIC_FIELD_STRENGTH, "MagneticFieldStrength"),
            (dcm_tags.MR_ACQUISITION_TYPE, "MRAcquisitionType"),
            (dcm_tags.FLIP_ANGLE, "FlipAngle"),
        ]:
            if dicom_key in dataset:
                bids[bids_key] = dataset.get(dicom_key, None).value

        # ms->s conversion for EchoTime (can be array)
        if dcm_tags.ECHO_TIME in dataset:
            echo_time = dataset.get(dcm_tags.ECHO_TIME, None).value
            bids["EchoTime"] = UnitConverterUtils.convert_milliseconds_to_seconds(echo_time)

        # ms->s conversion for RepetitionTimePreparation
        if dcm_tags.REPETITION_TIME in dataset:
            repetition_time = dataset.get(dcm_tags.REPETITION_TIME, None).value
            bids["RepetitionTimePreparation"] = UnitConverterUtils.convert_milliseconds_to_seconds(repetition_time)

        return bids 

    def convert_to_bids(self, dicom_dir: str, output_dir: str, bids_basename: str = "sub-01_asl", overwrite: bool = False):
        """
        Orchestrate the conversion from DICOM series to BIDS (NIfTI, JSON, TSV).
        """
        
        # 1. Convert DICOM to NIfTI
        nifti_path = DICOM2NiFTIConverter.dir_to_nifti(dicom_dir, output_dir, bids_basename, overwrite)

        # 2. Extract metadata and write JSON
        metadata = self.extract_bids_metadata()
        JSONWriter.write(metadata, os.path.join(output_dir, f"{bids_basename}.json"))

        # 3. Generate aslcontext.tsv
        context = self.generate_asl_context(nifti_path)
        TsvWriter.write(context, os.path.join(output_dir, f"{bids_basename}_aslcontext.tsv"))

        return {
            "nifti": nifti_path,
            "json": os.path.join(output_dir, f"{bids_basename}.json"),
            "aslcontext": os.path.join(output_dir, f"{bids_basename}_aslcontext.tsv"),
        }