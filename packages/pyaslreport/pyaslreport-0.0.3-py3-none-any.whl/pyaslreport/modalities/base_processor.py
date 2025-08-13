from abc import ABC, abstractmethod

class BaseProcessor(ABC):

    def __init__(self, data) -> None:
        """
        Initialize the BaseProcessor with the input data.

        :param data: The input data to be processed.
        """
        self.data = data

    @abstractmethod
    def process(self) -> str:
        """
        Process the input data.
        Must be implemented by all processors.

        :return: the report generated for the modality.
        """
        pass
