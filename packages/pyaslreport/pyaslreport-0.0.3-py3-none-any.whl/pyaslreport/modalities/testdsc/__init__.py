from . import processor, validator
from pyaslreport.modalities.registry import register_modality
from pyaslreport.enums import ModalityTypeValues

register_modality(
    name=ModalityTypeValues.DSC,
    processor_cls=processor.DSCProcessor,
    validator_cls=validator.DSCValidator
)
