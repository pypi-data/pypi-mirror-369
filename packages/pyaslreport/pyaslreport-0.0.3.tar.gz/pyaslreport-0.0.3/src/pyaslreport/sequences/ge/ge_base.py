from pyaslreport.sequences.base_sequence import BaseSequence
from pyaslreport.utils import dicom_tags_utils as dcm_tags

class GEBaseSequence(BaseSequence):
    @classmethod
    def is_ge_manufacturer(cls, dicom_header):
        """
        Check if the manufacturer contains GE or General Electric.
        
        Args:
            dicom_header: DICOM header dictionary
            
        Returns:
            bool: True if manufacturer contains GE or General Electric
        """
        manufacturer = dicom_header.get(dcm_tags.MANUFACTURER, "").value.strip().upper()
        return "GE" in manufacturer or "GENERAL ELECTRIC" in manufacturer

    def _extract_ge_common_metadata(self) -> dict:
        dataset = self.dicom_header
        bids_ge = {}
        # Direct GE-specific mappings
        if dcm_tags.GE_ASSET_R_FACTOR in dataset:
            bids_ge["AssetRFactor"] = dataset.get(dcm_tags.GE_ASSET_R_FACTOR, None).value
        if dcm_tags.GE_EFFECTIVE_ECHO_SPACING in dataset:
            bids_ge["EffectiveEchoSpacing"] = dataset.get(dcm_tags.GE_EFFECTIVE_ECHO_SPACING, None).value
        if dcm_tags.GE_ACQUISITION_MATRIX in dataset:
            bids_ge["AcquisitionMatrix"] = dataset.get(dcm_tags.GE_ACQUISITION_MATRIX, None).value
        if dcm_tags.GE_NUMBER_OF_EXCITATIONS in dataset:
            bids_ge["TotalAcquiredPairs"] = dataset.get(dcm_tags.GE_NUMBER_OF_EXCITATIONS, None).value
            
        # Derived fields
        # EffectiveEchoSpacing = EffectiveEchoSpacing * AssetRFactor * 1e-6
        if dcm_tags.GE_EFFECTIVE_ECHO_SPACING in dataset and dcm_tags.GE_ASSET_R_FACTOR in dataset:
            try:
                eff_echo = float(dataset.get(dcm_tags.GE_EFFECTIVE_ECHO_SPACING, None).value)
                asset = float(dataset.get(dcm_tags.GE_ASSET_R_FACTOR, None).value)
                bids_ge["EffectiveEchoSpacing"] = eff_echo * asset * 1e-6
            except Exception:
                pass

        # TotalReadoutTime = (AcquisitionMatrix[0] - 1) * EffectiveEchoSpacing
        if (
            dcm_tags.GE_ACQUISITION_MATRIX in dataset and
            isinstance(dataset.get(dcm_tags.GE_ACQUISITION_MATRIX, None).value, (list, tuple)) and
            len(dataset.get(dcm_tags.GE_ACQUISITION_MATRIX, None).value) > 0 and
            dcm_tags.GE_EFFECTIVE_ECHO_SPACING in bids_ge
        ):
            try:
                acq_matrix = dataset.get(dcm_tags.GE_ACQUISITION_MATRIX, None).value[0]
                eff_echo = bids_ge["EffectiveEchoSpacing"]
                bids_ge["TotalReadoutTime"] = (acq_matrix - 1) * eff_echo
            except Exception:
                pass
        
        # MRAcquisitionType default is 3D if not present
        if dcm_tags.MR_ACQUISITION_TYPE in dataset:
            bids_ge["MRAcquisitionType"] = dataset.get(dcm_tags.MR_ACQUISITION_TYPE, None).value
        else:
            bids_ge["MRAcquisitionType"] = "3D"

        # PulseSequenceType default is spiral if not present
        if dcm_tags.MR_ACQUISITION_TYPE in dataset:
            bids_ge["PulseSequenceType"] = dataset.get(dcm_tags.MR_ACQUISITION_TYPE, None).value
        else:
            bids_ge["PulseSequenceType"] = "spiral"
            
            
        # Virtal Parameters that applies to all GE sequences and not specifiied in the DICOM header
        bids_ge["BackgroundSuppression"] = True
        bids_ge["BackgroundSuppressionNumberPulses"] = 4
        
        
        # M0 scan detection and ASL context handling
        # For GE: Control/label subtraction is executed on scanner, only deltaM images saved
        # M0 scan is included by default in all acquisitions
        bids_ge["M0Type"] = "Included"
        
        # Check if CBF images are provided instead of deltaM/M0
        # This would indicate M0 scan is absent
        if self._is_cbf_image():
            bids_ge["M0Type"] = "Absent"
        
        return bids_ge
    
    def _is_cbf_image(self) -> bool:
        """
        Check if the current image is a CBF (Cerebral Blood Flow) image.
        CBF images indicate processed data where M0 scan would be absent.
        
        Returns:
            bool: True if this appears to be a CBF image
        """
        dataset = self.dicom_header
        
        # Check image type or series description for CBF indicators
        image_type = dataset.get(dcm_tags.IMAGE_TYPE, "").value if dcm_tags.IMAGE_TYPE in dataset else ""
        series_desc = dataset.get(dcm_tags.SERIES_DESCRIPTION, "").value if dcm_tags.SERIES_DESCRIPTION in dataset else ""
        
        # Common CBF indicators in GE sequences
        cbf_indicators = ["CBF", "PERFUSION", "FLOW", "ML/100G/MIN"]
        
        # Check if any CBF indicators are present
        combined_text = f"{image_type} {series_desc}".upper()
        return any(indicator in combined_text for indicator in cbf_indicators)
