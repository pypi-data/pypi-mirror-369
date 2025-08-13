from pyaslreport.sequences.base_sequence import BaseSequence
from pyaslreport.utils import dicom_tags_utils as dcm_tags

class SiemensBaseSequence(BaseSequence):
    @classmethod
    def is_siemens_manufacturer(cls, dicom_header):
        """
        Check if the manufacturer contains Siemens.
        
        Args:
            dicom_header: DICOM header dictionary
            
        Returns:
            bool: True if manufacturer contains Siemens
        """
        manufacturer = dicom_header.get(dcm_tags.MANUFACTURER, "").value.strip().upper()
        return "SIEMENS" in manufacturer or "SIEMENS HEALTHCARE" in manufacturer or "SIEMENS HEALHINEERS" in manufacturer


    def _extract_siemens_common_metadata(self) -> dict:
        d = self.dicom_header
        bids = {}
        # Direct GE-specific mappings
        if dcm_tags.GE_ASSET_R_FACTOR in d:
            bids["AssetRFactor"] = d.get(dcm_tags.GE_ASSET_R_FACTOR, None).value
        if dcm_tags.GE_EFFECTIVE_ECHO_SPACING in d:
            bids["EffectiveEchoSpacing"] = d.get(dcm_tags.GE_EFFECTIVE_ECHO_SPACING, None).value
        if dcm_tags.GE_ACQUISITION_MATRIX in d:
            bids["AcquisitionMatrix"] = d.get(dcm_tags.GE_ACQUISITION_MATRIX, None).value
        if dcm_tags.GE_NUMBER_OF_EXCITATIONS in d:
            bids["TotalAcquiredPairs"] = d.get(dcm_tags.GE_NUMBER_OF_EXCITATIONS, None).value
            
        # Derived fields
        # EffectiveEchoSpacing = EffectiveEchoSpacing * AssetRFactor * 1e-6
        if dcm_tags.GE_EFFECTIVE_ECHO_SPACING in d and dcm_tags.GE_ASSET_R_FACTOR in d:
            try:
                eff_echo = float(d.get(dcm_tags.GE_EFFECTIVE_ECHO_SPACING, None).value)
                asset = float(d.get(dcm_tags.GE_ASSET_R_FACTOR, None).value)
                bids["EffectiveEchoSpacing"] = eff_echo * asset * 1e-6
            except Exception:
                pass

        # TotalReadoutTime = (AcquisitionMatrix[0] - 1) * EffectiveEchoSpacing
        if (
            dcm_tags.GE_ACQUISITION_MATRIX in d and
            isinstance(d.get(dcm_tags.GE_ACQUISITION_MATRIX, None).value, (list, tuple)) and
            len(d.get(dcm_tags.GE_ACQUISITION_MATRIX, None).value) > 0 and
            dcm_tags.GE_EFFECTIVE_ECHO_SPACING in bids
        ):
            try:
                acq_matrix = d.get(dcm_tags.GE_ACQUISITION_MATRIX, None).value[0]
                eff_echo = bids["EffectiveEchoSpacing"]
                bids["TotalReadoutTime"] = (acq_matrix - 1) * eff_echo
            except Exception:
                pass
        
        # MRAcquisitionType default is 3D if not present
        if dcm_tags.MR_ACQUISITION_TYPE in d:
            bids["MRAcquisitionType"] = d.get(dcm_tags.MR_ACQUISITION_TYPE, None).value
        else:
            bids["MRAcquisitionType"] = "3D"

        # PulseSequenceType default is spiral if not present
        if dcm_tags.MR_ACQUISITION_TYPE in d:
            bids["PulseSequenceType"] = d.get(dcm_tags.MR_ACQUISITION_TYPE, None).value
        else:
            bids["PulseSequenceType"] = "spiral"

        return bids