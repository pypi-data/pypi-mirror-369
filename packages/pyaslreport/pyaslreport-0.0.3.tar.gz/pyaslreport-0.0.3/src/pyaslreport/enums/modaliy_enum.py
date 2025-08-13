from enum import Enum, unique

@unique
class ModalityTypeValues(Enum):
    """ Enumeration for different types of modalities. """
    ASL = 'ASL'
    DCE = 'DCE'
    DSC = 'DSC'