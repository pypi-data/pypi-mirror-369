import math
from pyaslreport.sequences.ge.asl.ge_asl_base import GEASLBase
from pyaslreport.utils import dicom_tags_utils as dcm_tags

class GEMultiPLD(GEASLBase):
    @classmethod
    def matches(cls, dicom_header):
        return (
            cls.is_ge_manufacturer(dicom_header) and
            dicom_header.get(dcm_tags.GE_INTERNAL_SEQUENCE_NAME, "").value.strip().lower() == "easl"
        )

    @classmethod
    def get_specificity_score(cls) -> int:
        """Higher specificity score because it checks for specific sequence name."""
        return 10

    def extract_bids_metadata(self):
        
        bids = self._extract_common_metadata()
        bids.update(self._extract_ge_common_metadata())
        bids.update(self._extract_ge_common_asl_metadata())

        dataset = self.dicom_header
        # ArterialSpinLabelingType is always 'PCASL'
        bids["ArterialSpinLabelingType"] = "PCASL"

        # Calculate LabelingDuration and PostLabelingDelay arrays
        npld = dataset.get(dcm_tags.GE_PRIVATE_CV6, None).value
        if npld is not None:
            try:
                npld = int(npld)
            except Exception:
                npld = None
                
        if npld == 1:
            # Single-PLD
            bids["LabelingDuration"] = dataset.get(dcm_tags.GE_PRIVATE_CV5, None).value
            bids["PostLabelingDelay"] = dataset.get(dcm_tags.GE_PRIVATE_CV4, None).value
        elif npld and npld > 1:
            # Multi-PLD
            cv4 = float(dataset.get(dcm_tags.GE_PRIVATE_CV4, 0).value)
            cv5 = float(dataset.get(dcm_tags.GE_PRIVATE_CV5, 0).value)
            cv7 = float(dataset.get(dcm_tags.GE_PRIVATE_CV7, 1).value)
            magnetic_field_strength = float(dataset.get(dcm_tags.MAGNETIC_FIELD_STRENGTH, 3).value)
            
            # T1 for blood
            T1 = 1.65 if magnetic_field_strength == 3 else 1.4
            
            # Linear calculation
            LD_lin = [cv5 / npld] * npld
            PLD_lin = [cv4 + i * LD_lin[0] for i in range(npld)]
            
            # Exponential calculation
            LD_exp = []
            PLD_exp = [cv4]
            Starget = npld * (1 - math.exp(-cv5 / T1)) * math.exp(-cv4 / T1)
            
            # Check if exponential calculation is mathematically valid
            exp_calculation_valid = True
            try:
                for i in range(npld):
                    if i == 0:
                        exp_factor = Starget * math.exp(PLD_exp[0] / T1)
                        if exp_factor >= 1:
                            exp_calculation_valid = False
                            break
                        LD_exp.append(-T1 * math.log(1 - exp_factor))
                    else:
                        PLD_exp.append(PLD_exp[i-1] + LD_exp[i-1])
                        exp_factor = Starget * math.exp(PLD_exp[i] / T1)
                        if exp_factor >= 1:
                            exp_calculation_valid = False
                            break
                        LD_exp.append(-T1 * math.log(1 - exp_factor))
            except (ValueError, OverflowError):
                exp_calculation_valid = False
            
            if cv7 == 1:
                bids["LabelingDuration"] = LD_lin
                bids["PostLabelingDelay"] = PLD_lin
            elif cv7 == 0 and exp_calculation_valid:
                bids["LabelingDuration"] = LD_exp
                bids["PostLabelingDelay"] = PLD_exp
            elif cv7 == 0 and not exp_calculation_valid:
                # Fall back to linear calculation if exponential fails
                bids["LabelingDuration"] = LD_lin
                bids["PostLabelingDelay"] = PLD_lin
            elif exp_calculation_valid:
                # Linear combination
                bids["LabelingDuration"] = [ld_lin * cv7 + ld_exp * (1 - cv7) for ld_lin, ld_exp in zip(LD_lin, LD_exp)]
                bids["PostLabelingDelay"] = [pld_lin * cv7 + pld_exp * (1 - cv7) for pld_lin, pld_exp in zip(PLD_lin, PLD_exp)]
            else:
                # Fall back to linear calculation if exponential fails
                bids["LabelingDuration"] = LD_lin
                bids["PostLabelingDelay"] = PLD_lin
        
        # ASLcontext: all deltaM, last one is m0scan
        bids["ASLContext"] = self._generate_asl_context(npld if npld else 2)
        
        return bids 