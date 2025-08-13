from pyaslreport.modalities.asl.validators.base_asl_validator import BaseASLValidator


class NumberArrayValidator(BaseASLValidator):
  """
  Validator for arrays of numerical values. Supports size checks, range validation, and ascending order checks.
  """

  def __init__(self, size_error=None, min_error=None, max_error=None, min_warning=None,
               max_warning=None, min_error_include=None, check_ascending=False):
    super().__init__()

    # Validate that the array has a specific number of elements
    if size_error is not None:
      self.add_error_rule(
        lambda x: isinstance(x, list) and all(isinstance(i, (int, float)) for i in x) and len(
          x) == size_error,
        f"Array must consist of exactly {size_error} numbers")

    if min_error is not None:
      self.add_error_rule(lambda x: all(i > min_error for i in x if isinstance(i, (int, float))),
                          f"All numbers must be > {min_error}")
    if max_error is not None:
      self.add_error_rule(lambda x: all(i < max_error for i in x if isinstance(i, (int, float))),
                          f"All numbers must be < {max_error}")
    if min_error_include is not None:
      self.add_error_rule(
        lambda x: all(i >= min_error_include for i in x if isinstance(i, (int, float))),
        f"All numbers must be >= {min_error_include}")
    if min_warning is not None:
      self.add_warning_rule(
        lambda x: all(i > min_warning for i in x if isinstance(i, (int, float))),
        f"Some numbers may be unusually low ({min_warning})")
    if max_warning is not None:
      self.add_warning_rule(
        lambda x: all(i < max_warning for i in x if isinstance(i, (int, float))),
        f"Some numbers may be unusually high ({max_warning})")

    # Optionally validate that the numbers in the array are in ascending order
    if check_ascending:
      self.add_error_rule(
        lambda x: sorted(x) == x,
        "Numbers in the array are not in ascending order")