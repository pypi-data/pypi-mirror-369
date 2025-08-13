from pyaslreport.modalities.asl.validators.base_asl_validator import BaseASLValidator


class BooleanValidator(BaseASLValidator):
  """
  Validator for boolean values. Ensures the value is either True or False.
  """

  def __init__(self):
    super().__init__()
    self.add_error_rule(lambda x: isinstance(x, bool), "Value must be a boolean (True or False)")