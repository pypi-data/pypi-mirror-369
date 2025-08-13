from pyaslreport.modalities.asl.validators.base_asl_validator import BaseASLValidator


class NumberValidator(BaseASLValidator):
  """
  Validator for numerical values. Supports validation of ranges, integer enforcement, and warnings.
  """

  def __init__(self, min_error=None, max_error=None, min_warning=None, max_warning=None,
               min_error_include=None, max_error_include=None, enforce_integer=False):
    super().__init__()

    if enforce_integer:
      self.add_error_rule(lambda x: isinstance(x, int), "Value must be an integer")

    if min_error is not None:
      self.add_error_rule(lambda x: x > min_error, f"Value must be > {min_error}")
    if max_error is not None:
      self.add_error_rule(lambda x: x < max_error, f"Value must be < {max_error}")
    if min_error_include is not None:
      self.add_error_rule(lambda x: x >= min_error_include, f"Value must be >= {min_error_include}")
    if max_error_include is not None:
      self.add_error_rule(lambda x: x <= max_error_include, f"Value must be <= {max_error_include}")
    if min_warning is not None:
      self.add_warning_rule(lambda x: x > min_warning, f"Value is unusually low ({min_warning})")
    if max_warning is not None:
      self.add_warning_rule(lambda x: x < max_warning, f"Value is unusually high ({max_warning})")