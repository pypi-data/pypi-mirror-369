from . import processor, validator
from pyaslreport.modalities.registry import register_modality
from pyaslreport.enums import ModalityTypeValues

register_modality(
    name=ModalityTypeValues.ASL,
    processor_cls=processor.ASLProcessor,
    validator_cls=validator.ASLValidator
)
