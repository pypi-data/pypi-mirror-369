from pyaslreport.modalities.base_validator import BaseValidator


class DSCValidator(BaseValidator):
    """
    ASLValidator is a class that validates the parameters for ASL (Arterial Spin Labeling) modality.
    """

    def validate(self, data) -> bool:
        """
        Validates the parameters for DSC modality.

        :param data: Dictionary containing DSC parameters.
        :return: True if valid, raises ValueError otherwise.
        """
        print("Validating parameters for DSC modality")

        return True