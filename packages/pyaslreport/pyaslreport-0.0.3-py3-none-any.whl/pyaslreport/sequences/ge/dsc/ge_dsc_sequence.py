from pyaslreport.sequences.ge.ge_base import GEBaseSequence
import pydicom


class GEDSCSequence(GEBaseSequence):
    
    @classmethod
    def matches(cls, dicom_header):
        return cls.is_ge_manufacturer(dicom_header)
        
    def extract_bids_metadata(self) -> dict:
        """Extract and convert DICOM metadata to BIDS fields."""

        print('processing GE DSC sequence')
        
        return {
            "dsc": "dsc params"
        }