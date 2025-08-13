import pydicom
from pyaslreport.sequences.siemens.siemens_base import SiemensBaseSequence


class SiemensDSCSequence(SiemensBaseSequence):

    @classmethod
    def matches(cls, dicom_header):
        return cls.is_siemens_manufacturer(dicom_header)

    def extract_bids_metadata(self) -> dict:
        """Extract and convert DICOM metadata to BIDS fields."""

        print('processing Siemens DSC sequence')
        
        return {
            "dsc": "dsc params"
        }