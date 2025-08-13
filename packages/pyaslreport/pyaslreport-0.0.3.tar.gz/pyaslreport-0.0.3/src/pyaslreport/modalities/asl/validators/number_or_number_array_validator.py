from pyaslreport.modalities.asl.validators.base_asl_validator import BaseASLValidator
from pyaslreport.modalities.asl.validators.number_array_validator import NumberArrayValidator
from pyaslreport.modalities.asl.validators.number_validator import NumberValidator


class NumberOrNumberArrayValidator(BaseASLValidator):
  """
  Validator for single numbers or arrays of numbers. Combines the functionality of NumberValidator and NumberArrayValidator.
  """

  def __init__(self, size_error=None, min_error=None, max_error=None, min_warning=None,
               max_warning=None, min_error_include=None, check_ascending=False):
    super().__init__()
    self.number_validator = NumberValidator(
      min_error=min_error,
      max_error=max_error,
      min_warning=min_warning,
      max_warning=max_warning,
      min_error_include=min_error_include
    )
    self.array_validator = NumberArrayValidator(
      size_error=size_error,
      min_error=min_error,
      max_error=max_error,
      min_warning=min_warning,
      max_warning=max_warning,
      min_error_include=min_error_include,
      check_ascending=check_ascending
    )

  def validate(self, value):
    """
    Validates either a single number or an array of numbers, returning appropriate messages for errors or warnings.
    """
    if isinstance(value, (int, float)):
      return self.number_validator.validate(value)
    elif isinstance(value, list):
      return self.array_validator.validate(value)
    else:
      return "Value must be a number or an array of numbers", None, None, None, None, None