from pyaslreport.modalities.asl.validators.base_asl_validator import BaseASLValidator


class StringValidator(BaseASLValidator):
  """
  Validator for string values. Validates against a list of allowed values, with optional major error enforcement.
  """

  def __init__(self, allowed_values=None, major_error=False):
    super().__init__()
    # Convert allowed_values to lower case for case-insensitive comparison
    if allowed_values:
      self.allowed_values = {value.lower() for value in allowed_values}
      if major_error:
        self.add_major_error_rule(lambda x: x.lower() in self.allowed_values,
                                  f"Value must be one of {allowed_values}, case-insensitive")
      else:
        self.add_error_rule(lambda x: x.lower() in self.allowed_values,
                            f"Value must be one of {allowed_values}, case-insensitive")