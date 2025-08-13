import yaml
import os

from pyaslreport.core.exceptions import ConfigurationError

class YamlReader:
    """
    A class to read YAML files.
    """

    @staticmethod
    def read(file_path) -> dict:
        """
        Load a YAML file from the given path.
        Args:
         file_path (str): Path to the YAML file to be read.
        Returns:
            dict: Parsed content of the YAML file.
        """

        if not os.path.exists(file_path):
            raise ConfigurationError(f"Config file not found: {file_path}")

        with open(file_path, 'r') as f:
            content = yaml.safe_load(f)

        if not isinstance(content, dict):
            raise ConfigurationError(f"Invalid config file: {file_path}")

        return content

