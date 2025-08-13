
class ValidationUtils:

    @staticmethod
    def is_valid_number(val):
        """
        Check if the value is a valid number (int or float).
        Args:
         val: The value to check.
        Returns:
            True if the value is a valid number, False otherwise.
        """
        return isinstance(val, (int, float))

    @staticmethod
    def is_valid_list(val):
        """
        Check if the value is a valid list of numbers.
        Args:
             val: The value to check.
        Returns:
            True if the value is a list of valid numbers, False otherwise.
        """
        return isinstance(val, list) and all(ValidationUtils.is_valid_number(v) for v in val)