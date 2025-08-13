from operator import truediv
from pyaslreport.sequences.ge.ge_base import GEBaseSequence
from pyaslreport.utils import dicom_tags_utils as dcm_tags

class GEASLBase(GEBaseSequence):
    
    def _extract_ge_common_asl_metadata(self):
        bids_ge_asl = {}

        bids_ge_asl["BackgroundSuppression"] = True
        bids_ge_asl["BackgroundSuppressionNumberPulses"] = 4
        
        # M0 scan detection and ASL context handling
        # For GE: Control/label subtraction is executed on scanner, only deltaM images saved
        # M0 scan is included by default in all acquisitions
        bids_ge_asl["M0Type"] = "Included"
        
        # Check if CBF images are provided instead of deltaM/M0
        # This would indicate M0 scan is absent
        if self._is_cbf_image():
            bids_ge_asl["M0Type"] = "Absent"
        
        return bids_ge_asl

    def _get_volume_type(self) -> str:
        """
        Determine the volume type based on DICOM ImageType tag.
        
        Returns:
            str: "deltaM", "m0scan", or "cbf"
        """
        dataset = self.dicom_header
        image_type = dataset.get(dcm_tags.IMAGE_TYPE, "").value if dcm_tags.IMAGE_TYPE in dataset else ""
        
        if isinstance(image_type, (list, tuple)):
            image_type_str = " ".join(str(x).upper() for x in image_type)
        else:
            image_type_str = str(image_type).upper()
        
        # CBF patterns
        cbf_patterns = [
            ["DERIVED", "PRIMARY", "CBF", "CBF"],
            ["DERIVED", "PRIMARY", "CBF", "CBF", "REAL"]
        ]
        
        # M0 scan patterns  
        m0_patterns = [
            ["ORIGINAL", "PRIMARY", "ASL", "REAL"],
            ["ORIGINAL", "PRIMARY", "ASL"]
        ]
        
        # deltaM patterns
        deltam_patterns = [
            ["DERIVED", "PRIMARY", "ASL", "PERFUSION", "ASL"],
            ["DERIVED", "PRIMARY", "ASL", "PERFUSION", "ASL", "REAL"],
            ["DERIVED", "PRIMARY", "ASL", "PERFUSION_ASL"]
        ]
        
        # Check patterns
        for pattern in cbf_patterns:
            if all(tag in image_type_str for tag in pattern):
                return "cbf"
                
        for pattern in m0_patterns:
            if all(tag in image_type_str for tag in pattern):
                return "m0scan"
                
        for pattern in deltam_patterns:
            if all(tag in image_type_str for tag in pattern):
                return "deltaM"
        
        # Default assumption for GE
        return "deltaM"

    def _is_cbf_image(self) -> bool:
        """
        Check if the current image is a CBF (Cerebral Blood Flow) image.
        CBF images indicate processed data where M0 scan would be absent.
        
        Returns:
            bool: True if this appears to be a CBF image
        """
        return self._get_volume_type() == "cbf"
        
    def _generate_asl_context(self, npld: int) -> list:
        """
        Generate ASLContext based on volume type and number of PLDs.
        Normal order: deltaM followed by M0 scan for each PLD.
        
        Args:
            npld: Number of post-labeling delays
            
        Returns:
            list: ASLContext array
        """
        volume_type = self._get_volume_type()
        
        if volume_type == "cbf":
            # CBF images don't have M0 scans
            return ["deltaM"] * npld
        else:
            # Normal case: deltaM + M0 for each PLD, but summed on scanner
            # Results in single deltaM followed by single M0
            if npld == 1:
                return ["deltaM", "m0scan"]
            else:
                # Multi-PLD: all deltaM (summed), last one is m0scan
                return ["deltaM"] * (npld - 1) + ["m0scan"]