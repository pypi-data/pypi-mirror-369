class BaseASLValidator:
  """
  Base class for all validators. Manages rules for major errors, errors, and warnings.
  """

  def __init__(self):
    self.major_error_rules = []
    self.error_rules = []
    self.warning_rules = []

  def add_major_error_rule(self, func, major_error_msg):
    """Adds a major error rule with a corresponding message."""
    self.major_error_rules.append((func, major_error_msg))

  def add_error_rule(self, func, error_msg):
    """Adds an error rule with a corresponding message."""
    self.error_rules.append((func, error_msg))

  def add_warning_rule(self, func, warning_msg):
    """Adds a warning rule with a corresponding message."""
    self.warning_rules.append((func, warning_msg))

  def validate(self, value):
    """Validates the value against the rules, returning the appropriate error or warning."""
    for func, major_error_msg in self.major_error_rules:
      if not func(value):
        return major_error_msg, major_error_msg, None, None, None, None
    for func, error_msg in self.error_rules:
      if not func(value):
        return None, None, error_msg, error_msg, None, None
    for func, warning_msg in self.warning_rules:
      if not func(value):
        return None, None, None, None, warning_msg, warning_msg
    return None, None, None, None, None, None

