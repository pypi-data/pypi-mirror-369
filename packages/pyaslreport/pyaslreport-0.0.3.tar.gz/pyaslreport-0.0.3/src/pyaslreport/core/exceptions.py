class ASLParamGeneratorError(Exception):
    """Base class for all exceptions in the project."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class ReaderError(ASLParamGeneratorError):
    """Raised when reading input data fails."""
    pass

class WriterError(ASLParamGeneratorError):
    """Raised when writing output data fails."""
    pass

class ProcessorError(ASLParamGeneratorError):
    """Raised during processing stage failures."""
    pass

class ConfigurationError(ASLParamGeneratorError):
    """Raised for configuration-related issues."""
    pass


class InvalidFileFormatError(ASLParamGeneratorError):
    """Raised when the file format is invalid or unsupported."""
    pass
