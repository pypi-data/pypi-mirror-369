from .math_utils import MathUtils
from .validation_utils import ValidationUtils


class UnitConverterUtils:
    SECOND_TO_MILLISECOND = 1000

    @staticmethod
    def convert_to_milliseconds(values: int | float | list[int | float]) -> int | float | list[int | float]:
        """
        Convert seconds to milliseconds and round close values to integers.
        Handles single numeric values or lists of values.
        Args:
            values (int | float | list[int | float]): The value(s) in seconds to convert.
        Returns:
            int | float | list[int | float]: The converted value(s) in milliseconds.
        """
        def convert_value(value):
            if isinstance(value, (int, float)):
                return MathUtils.round_if_close(value * UnitConverterUtils.SECOND_TO_MILLISECOND)
            elif isinstance(value, list):
                return [MathUtils.round_if_close(v * UnitConverterUtils.SECOND_TO_MILLISECOND) for v in value]
            return value

        if ValidationUtils.is_valid_number(values):
            return convert_value(values)
        elif ValidationUtils.is_valid_list(values):
            return [convert_value(value) for value in values]
        else:
            raise TypeError("Input must be an int, float, or list of int/float.")


    def convert_milliseconds_to_seconds(values: int | float | list[int | float]) -> int | float | list[int | float]:
        """
        Convert milliseconds to seconds and round close values to integers.
        Handles single numeric values or lists of values.
        """
        def convert_value(value):
                return value / 1000.0

        if ValidationUtils.is_valid_number(values):
            return convert_value(values)
        elif ValidationUtils.is_valid_list(values):
            return [convert_value(value) for value in values]
        else:
            raise TypeError("Input must be an int, float, or list of int/float.")

