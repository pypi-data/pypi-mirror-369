from pyaslreport.modalities.asl.validators.json_validator import JSONValidator
from pyaslreport.modalities.base_validator import BaseValidator
from pyaslreport.core.config import config


class ASLValidator(BaseValidator):
    """
    ASLValidator is a class that validates the parameters for ASL (Arterial Spin Labeling) modality.
    """

    def validate(self, data):
        major_error_schema_alias = config['schemas']['major_error_schema']
        required_validator_schema_alias = config['schemas']['required_validator_schema']
        required_condition_schema_alias = config['schemas']['required_condition_schema']
        recommended_validator_schema_alias = config['schemas']['recommended_validator_schema']
        recommended_condition_schema_alias = config['schemas']['recommended_condition_schema']
        consistency_schema_alias = config['schemas']['consistency_schema']

        json_validator = JSONValidator(major_error_schema_alias, required_validator_schema_alias,
                                       required_condition_schema_alias,
                                       recommended_validator_schema_alias,
                                       recommended_condition_schema_alias,
                                       consistency_schema_alias)

        major_errors, major_errors_concise, errors, errors_concise, warnings, warnings_concise, values \
            = json_validator.validate(data["data"], data["filenames"])

        return major_errors, major_errors_concise, errors, errors_concise, warnings, warnings_concise, values
