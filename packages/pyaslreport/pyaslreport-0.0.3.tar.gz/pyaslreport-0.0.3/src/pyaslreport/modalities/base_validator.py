from abc import ABC, abstractmethod

class BaseValidator(ABC):
    @abstractmethod
    def validate(self, data) -> bool:
        """
        Validates the input data.
        Must be implemented by all validators.

        """
        pass
