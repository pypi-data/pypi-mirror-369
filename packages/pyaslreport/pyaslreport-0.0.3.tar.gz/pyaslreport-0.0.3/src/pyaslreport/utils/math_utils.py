class MathUtils:

    @staticmethod
    def round_if_close(val, decimal_places=3):
        """
        Round a value to a specified number of decimal places if it is close to an integer.
        Args:
            val (int | float): The value to round.
            decimal_places (int): The number of decimal places to round to.
        Returns:
            int | float: The rounded value if close to an integer, otherwise the original value.
        """
        rounded_val = round(val, decimal_places)
        if abs(val - round(val)) < 1e-6:
            return round(val)
        return rounded_val
