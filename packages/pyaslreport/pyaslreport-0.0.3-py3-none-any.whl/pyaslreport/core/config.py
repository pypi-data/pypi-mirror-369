import os

from pyaslreport.io.readers.yaml_reader import YamlReader


class Config:
    """
    Configuration loader for the ASL Report package.
    This class is responsible for loading the configuration settings from YAML files.
    It reads allowed file types and schemas from specified directories.
    Attributes:
        config_dir (str): The directory where configuration files are stored.
        allowed_file_types_path (str): Path to the allowed file types YAML file.
        schemas_dir (str): Directory containing schema YAML files.

    Methods:
        _load_schemas: Loads all YAML schema files from the schemas directory.
        load: Loads the configuration, including allowed file types and schemas.
    """
    def __init__(self, config_dir):
        self.config_dir = config_dir
        self.allowed_file_types_path = os.path.join(config_dir, 'allowed_file_types.yaml')
        self.schemas_dir = os.path.join(config_dir, 'schemas')


    def _load_schemas(self) -> dict:
        """
        Load all YAML schema files from the schemas directory.
        Use the top-level key inside each YAML file as the schema name.
        Returns: A dictionary where keys are schema names and values are the parsed schema content.
        """
        schemas = {}
        for root, _, files in os.walk(self.schemas_dir):
            for file in files:
                if file.endswith('.yaml') or file.endswith('.yml'):
                    file_path = os.path.join(root, file)
                    content = YamlReader.read(file_path)
                    if isinstance(content, dict) and len(content) == 1:
                        key = next(iter(content))
                        schemas[key] = content[key]
                    else:
                        # fallback: use file name without extension
                        schema_name = os.path.splitext(file)[0]
                        schemas[schema_name] = content
        return schemas

    def load(self) -> dict:
        """
        Load the configuration, including allowed file types and schemas.
        Returns:  A dictionary containing allowed file types and schemas.
        """
        allowed_file_types = YamlReader.read(self.allowed_file_types_path)
        schemas = self._load_schemas()

        return {
            'allowed_file_type': allowed_file_types['allowed_file_types'],
            'paths': allowed_file_types['paths'],
            'schemas': schemas
        }


# Global config instance
CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'config')
config_loader = Config(CONFIG_DIR)
config = config_loader.load()
