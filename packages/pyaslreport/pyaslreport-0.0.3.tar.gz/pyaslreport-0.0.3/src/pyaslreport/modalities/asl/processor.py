import json
import math
import os
from typing import Any, Dict, List, Tuple, Optional
from dataclasses import dataclass

from pyaslreport.converters.dicom_to_nifti_converter import DICOM2NiFTIConverter
from pyaslreport.io.readers.nifti_reader import NiftiReader
from pyaslreport.io.readers.file_reader import FileReader
from pyaslreport.modalities.asl.report_generator import ReportGenerator
from pyaslreport.modalities.asl.utils import ASLUtils
from pyaslreport.modalities.asl.validator import ASLValidator
from pyaslreport.modalities.base_processor import BaseProcessor
from pyaslreport.modalities.asl.constants import DURATION_OF_EACH_RFBLOCK
from pyaslreport.utils.unit_conversion_utils import UnitConverterUtils
from pyaslreport.core.config import config


@dataclass
class ProcessingContext:
    """Data class to hold processing context and state."""
    asl_json_data: List[Dict[str, Any]]
    m0_prep_times_collection: List[Any]
    errors: List[str]
    warnings: List[str]
    all_absent: bool
    bs_all_off: bool
    m0_type: Optional[str]
    global_pattern: Optional[str]
    total_acquired_pairs: Optional[int]
    nifti_slice_number: int


class ASLProcessor(BaseProcessor):
    """
    Class for processing ASL (Arterial Spin Labeling) data.
    This class inherits from BaseProcessor and implements the process method to handle ASL report generation.
    Works with user-provided file paths without filename dependencies.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize the ASLProcessor with the input data.

        Args:
            data: The input data to be processed. Expected format:
                {
                    "files": [str, ...],           # List of file paths
                    "dcm_files": [str, ...],       # List of DICOM file paths (optional)
                    "nifti_file": str,             # NIfTI file path
                }
        """
        super().__init__(data)

    def process(self) -> Dict[str, Any]:
        """
        Main processing method that orchestrates the ASL data processing workflow.
        
        Returns:
            Dictionary containing processing results including reports, errors, and parameters.
        """
        self._validate_input_data()
        
        # Step 1: Convert DICOM files if present (in-place, no temp storage)
        nifti_file, file_format = self._convert_dicom_files()
        
        # Step 2: Group and organize files using user-provided paths
        grouped_files = self._group_files(file_format)
        
        # Step 3: Read NIfTI file and get slice information
        nifti_slice_number = self._get_nifti_slice_number(nifti_file)
        
        # Step 4: Process ASL JSON data
        context = self._process_asl_json_data(grouped_files, nifti_slice_number)
        
        # Step 5: Validate M0 data and TSV files
        self._validate_m0_and_tsv_data(grouped_files, context, file_format)
        
        # Step 6: Run validation and generate reports
        return self._generate_reports_and_results(context)

    def _validate_input_data(self) -> None:
        """Validate that input data contains required files."""
        if not self.data.get("files") and not self.data.get("dcm_files"):
            raise ValueError("No files provided for ASL processing.")

    def _convert_dicom_files(self) -> Tuple[str, str]:
        """
        Convert DICOM files to NIfTI format if present.
        Uses user-provided paths without creating temporary storage.
        
        Returns:
            Tuple of (nifti_file_path, file_format)
        """
        dcm_files = self.data.get("dcm_files", [])
        nifti_file = self.data.get("nifti_file")
        
        if not dcm_files:
            # No DICOM files, use existing NIfTI file
            if not self.data.get("files"):
                raise RuntimeError("Neither DICOM nor NIfTI files were found.")
            return str(nifti_file), "nifti"
        
        # Convert DICOM files using the converter
        converted_files, new_filenames, nifti_file, file_format, error = DICOM2NiFTIConverter.convert(
            dcm_files, nifti_file
        )

        if converted_files:
            self.data["files"].extend(converted_files)

        if error == "No DICOM files found." and not self.data.get("files"):
            raise RuntimeError("Neither DICOM nor NIfTI files were found.")
        elif error != "No DICOM files found." and error:
            raise RuntimeError(f"Error during conversion: {error}")

        return str(nifti_file), str(file_format)

    def _group_files(self, file_format: str) -> List[Dict[str, Any]]:
        """
        Group files by type using user-provided paths.
        Extracts filenames from paths when needed.
        
        Args:
            file_format: Format of the input files.
            
        Returns:
            List of grouped files with their data loaded.
        """
        files = self.data.get("files", [])
        
        grouped_files = []
        current_group = {'asl_json': None, 'm0_json': None, 'tsv': None}

        for filepath in files:
            # Extract filename from path
            filename = os.path.basename(filepath)
            
            if not filename.endswith(('.json', '.tsv')):
                raise ValueError(f"Unsupported file format: {filename}")

            # Read file data directly from user-provided path
            data = FileReader.read(filepath)

            if filename.endswith('m0scan.json') or (('m0' in filename) and file_format == "dicom"):
                current_group['m0_json'] = (filename, data)
            elif (filename.endswith('asl.json') and file_format == "nifti") or (
                    filename.endswith('.json') and file_format == "dicom"):
                if current_group['asl_json']:
                    grouped_files.append(current_group)
                current_group = {'asl_json': (filename, data), 'm0_json': None, 'tsv': None}
            elif filename.endswith('.tsv'):
                current_group['tsv'] = (filename, data)

        if current_group['asl_json']:
            grouped_files.append(current_group)

        return grouped_files

    def _get_nifti_slice_number(self, nifti_file: str) -> int:
        """
        Read NIfTI file and extract slice number.
        
        Args:
            nifti_file: Path to the NIfTI file.
            
        Returns:
            Number of slices in the NIfTI file.
        """
        nifti_img = NiftiReader.read(nifti_file)
        return nifti_img.shape[2]

    def _process_asl_json_data(self, grouped_files: List[Dict[str, Any]], nifti_slice_number: int) -> ProcessingContext:
        """
        Process ASL JSON data and extract metadata.
        
        Args:
            grouped_files: List of grouped files.
            nifti_slice_number: Number of slices in NIfTI file.
            
        Returns:
            ProcessingContext containing extracted data and metadata.
        """
        asl_json_data = []
        m0_prep_times_collection = []
        errors, warnings, all_absent, bs_all_off = [], [], True, True

        # Extract ASL JSON data from grouped files
        for group in grouped_files:
            if group['asl_json'] is not None:
                asl_filename, asl_data = group['asl_json']
                asl_json_data.append(asl_data)

                # Update metadata flags
                m0_type = asl_data.get("M0Type")
                if m0_type != "Absent":
                    all_absent = False
                if asl_data.get("BackgroundSuppression", []):
                    bs_all_off = False

        # Normalize ASL data (convert units, rename fields, etc.)
        self._normalize_asl_data(asl_json_data)

        return ProcessingContext(
            asl_json_data=asl_json_data,
            m0_prep_times_collection=m0_prep_times_collection,
            errors=errors,
            warnings=warnings,
            all_absent=all_absent,
            bs_all_off=bs_all_off,
            m0_type=None,
            global_pattern=None,
            total_acquired_pairs=None,
            nifti_slice_number=nifti_slice_number
        )

    def _normalize_asl_data(self, asl_json_data: List[Dict[str, Any]]) -> None:
        """
        Normalize ASL data by converting units and renaming fields.
        
        Args:
            asl_json_data: List of ASL JSON data dictionaries.
        """
        for session in asl_json_data:
            self._rename_fields(session)
            self._convert_units_to_milliseconds(session)
            session['PLDType'] = ASLUtils.determine_pld_type(session)

    def _rename_fields(self, session: Dict[str, Any]) -> None:
        """
        Rename fields in ASL session data to standard names.
        
        Args:
            session: ASL session data dictionary.
        """
        field_mappings = {
            'RepetitionTime': 'RepetitionTimePreparation',
            'InversionTime': 'PostLabelingDelay',
            'BolusDuration': 'BolusCutOffDelayTime',
            'InitialPostLabelDelay': 'PostLabelingDelay'
        }
        
        for old_key, new_key in field_mappings.items():
            if old_key in session:
                session[new_key] = session[old_key]
                del session[old_key]

        # Handle NumRFBlocks special case
        if 'NumRFBlocks' in session:
            session['LabelingDuration'] = session['NumRFBlocks'] * DURATION_OF_EACH_RFBLOCK

    def _convert_units_to_milliseconds(self, session: Dict[str, Any]) -> None:
        """
        Convert time-related fields from seconds to milliseconds.
        
        Args:
            session: ASL session data dictionary.
        """
        time_fields = [
            'EchoTime', 'RepetitionTimePreparation', 'LabelingDuration',
            'BolusCutOffDelayTime', 'BackgroundSuppressionPulseTime', 'PostLabelingDelay'
        ]
        
        for key in time_fields:
            if key in session:
                session[key] = UnitConverterUtils.convert_to_milliseconds(session[key])

    def _validate_m0_and_tsv_data(self, grouped_files: List[Dict[str, Any]], context: ProcessingContext, file_format: str) -> None:
        """
        Validate M0 data and TSV files, updating context with results.
        
        Args:
            grouped_files: List of grouped files.
            context: Processing context to update.
            file_format: Format of input files.
        """
        for i, group in enumerate(grouped_files):
            if group['asl_json'] is not None:
                asl_filename, asl_data = group['asl_json']
                context.m0_type = asl_data.get("M0Type")

                self._validate_m0_data(group, context, asl_filename, asl_data)
                self._validate_tsv_data(group, context, asl_filename, asl_data, file_format)

    def _validate_m0_data(self, group: Dict[str, Any], context: ProcessingContext, asl_filename: str, asl_data: Dict[str, Any]) -> None:
        """
        Validate M0 data and check for inconsistencies.
        
        Args:
            group: Group of files containing M0 data.
            context: Processing context to update.
            asl_filename: Name of ASL file.
            asl_data: ASL data dictionary.
        """
        if group['m0_json'] is not None:
            m0_filename, m0_data = group['m0_json']
            
            # Convert M0 time units
            for key in ['EchoTime', 'RepetitionTimePreparation', 'RepetitionTime']:
                if key in m0_data:
                    m0_data[key] = UnitConverterUtils.convert_to_milliseconds(m0_data[key])

            # Validate M0 type consistency
            if context.m0_type == "Absent":
                context.errors.append(
                    f"Error: M0 type specified as 'Absent' for '{asl_filename}', but '{m0_filename}' is present"
                )
            elif context.m0_type == "Included":
                context.errors.append(
                    f"Error: M0 type specified as 'Included' for '{asl_filename}', but '{m0_filename}' is present"
                )

            # Compare parameters between ASL and M0
            params_asl, params_m0 = ASLUtils.extract_params(asl_data), ASLUtils.extract_params(m0_data)
            comparison_errors, comparison_warnings = ASLUtils.compare_params(params_asl, params_m0, asl_filename, m0_filename)
            context.errors.extend(comparison_errors)
            context.warnings.extend(comparison_warnings)

            # Collect M0 preparation times
            m0_prep_time = m0_data.get("RepetitionTimePreparation", [])
            context.m0_prep_times_collection.append(m0_prep_time)
        else:
            if context.m0_type == "Separate":
                context.errors.append(
                    f"Error: M0 type specified as 'Separate' for '{asl_filename}', but m0scan.json is not provided."
                )

    def _validate_tsv_data(self, group: Dict[str, Any], context: ProcessingContext, asl_filename: str, asl_data: Dict[str, Any], file_format: str) -> None:
        """
        Validate TSV data and analyze volume types.
        
        Args:
            group: Group of files containing TSV data.
            context: Processing context to update.
            asl_filename: Name of ASL file.
            asl_data: ASL data dictionary.
            file_format: Format of input files.
        """
        if group['tsv'] is not None:
            tsv_filename, tsv_data = group['tsv']
            self._analyze_tsv_volume_types(tsv_data, context, asl_filename, asl_data, tsv_filename)
        elif file_format == "nifti":
            context.errors.append(f"Error: 'aslcontext.tsv' is missing for {asl_filename}")
        else:
            # Handle DICOM input case
            self._analyze_dicom_repetitions(asl_data, context)

    def _analyze_tsv_volume_types(self, tsv_data: List[str], context: ProcessingContext, asl_filename: str, asl_data: Dict[str, Any], tsv_filename: str) -> None:
        """
        Analyze volume types in TSV data and validate M0 scans.
        
        Args:
            tsv_data: TSV data as list of strings.
            context: Processing context to update.
            asl_filename: Name of ASL file.
            asl_data: ASL data dictionary.
            tsv_filename: Name of TSV file.
        """
        m0scan_count = sum(1 for line in tsv_data if line.strip() == "m0scan")
        volume_types = [line.strip() for line in tsv_data if line.strip()]
        pattern, total_acquired_pairs = ASLUtils.analyze_volume_types(volume_types)
        asl_data['TotalAcquiredPairs'] = total_acquired_pairs
        context.total_acquired_pairs = total_acquired_pairs

        # Update global pattern
        if context.global_pattern is None:
            context.global_pattern = pattern
        elif context.global_pattern != pattern:
            context.global_pattern = "control-label (there's no consistent control-label or label-control order)"

        # Validate M0 scan consistency
        self._validate_m0scan_consistency(m0scan_count, context, asl_filename, tsv_filename, asl_data)

    def _validate_m0scan_consistency(self, m0scan_count: int, context: ProcessingContext, asl_filename: str, tsv_filename: str, asl_data: Dict[str, Any]) -> None:
        """
        Validate consistency between M0 scan count and M0 type.
        
        Args:
            m0scan_count: Number of M0 scans found in TSV.
            context: Processing context to update.
            asl_filename: Name of ASL file.
            tsv_filename: Name of TSV file.
            asl_data: ASL data dictionary.
        """
        if m0scan_count > 0:
            if context.m0_type == "Absent":
                context.errors.append(
                    f"Error: m0 type is specified as 'Absent' for '{asl_filename}', but '{tsv_filename}' contains m0scan."
                )
            elif context.m0_type == "Separate":
                context.errors.append(
                    f"Error: m0 type is specified as 'Separate' for '{asl_filename}', but '{tsv_filename}' contains m0scan."
                )
            else:
                self._handle_m0scan_timing(asl_data, m0scan_count, context, asl_filename, tsv_filename)
        else:
            self._handle_no_m0scan_warnings(context, asl_filename, asl_data)

    def _handle_m0scan_timing(self, asl_data: Dict[str, Any], m0scan_count: int, context: ProcessingContext, asl_filename: str, tsv_filename: str) -> None:
        """
        Handle timing calculations for M0 scans.
        
        Args:
            asl_data: ASL data dictionary.
            m0scan_count: Number of M0 scans.
            context: Processing context to update.
            asl_filename: Name of ASL file.
            tsv_filename: Name of TSV file.
        """
        repetition_times = asl_data.get("RepetitionTimePreparation", [])
        if not isinstance(repetition_times, list):
            repetition_times = [repetition_times]

        repetition_times_max = max(repetition_times)
        repetition_times_min = min(repetition_times)

        if len(repetition_times) > m0scan_count:
            context.m0_prep_times_collection.append(repetition_times[0])
            asl_data["RepetitionTimePreparation"] = repetition_times[m0scan_count:]
        elif (repetition_times_max - repetition_times_min) < 10e-5:
            context.m0_prep_times_collection.append(repetition_times[0])
            asl_data["RepetitionTimePreparation"] = repetition_times[0]
        elif len(repetition_times) < m0scan_count:
            context.errors.append(
                f"Error: 'RepetitionTimePreparation' array in ASL file '{asl_filename}' is shorter "
                f"than the number of 'm0scan' in TSV file '{tsv_filename}'"
            )

    def _handle_no_m0scan_warnings(self, context: ProcessingContext, asl_filename: str, asl_data: Dict[str, Any]) -> None:
        """
        Handle warnings when no M0 scan is provided but background suppression is enabled.
        
        Args:
            context: Processing context to update.
            asl_filename: Name of ASL file.
            asl_data: ASL data dictionary.
        """
        if asl_data.get("BackgroundSuppression"):
            if asl_data.get("BackgroundSuppressionPulseTime"):
                context.warnings.append(
                    f"For {asl_filename}, no M0 is provided and BS pulses with known timings are on. "
                    f"BS-pulse efficiency has to be calculated to enable absolute quantification."
                )
            else:
                context.warnings.append(
                    f"For {asl_filename}, no M0 is provided and BS pulses with unknown timings are on, "
                    f"only a relative quantification is possible."
                )

    def _analyze_dicom_repetitions(self, asl_data: Dict[str, Any], context: ProcessingContext) -> None:
        """
        Analyze repetitions for DICOM input.
        
        Args:
            asl_data: ASL data dictionary.
            context: Processing context to update.
        """
        if 'lRepetitions' in asl_data:
            context.total_acquired_pairs = math.ceil(int(asl_data['lRepetitions']) / 2)
            asl_data['TotalAcquiredPairs'] = context.total_acquired_pairs
        context.global_pattern = "control-label"

    def _generate_reports_and_results(self, context: ProcessingContext) -> Dict[str, Any]:
        """
        Generate validation reports and final results.
        
        Args:
            context: Processing context containing all extracted data.
            
        Returns:
            Dictionary containing all processing results.
        """
        # Prepare data for validation
        validation_data = {
            "data": context.asl_json_data,
            "filenames": [f"asl_{i}.json" for i in range(len(context.asl_json_data))],
        }

        # Run validation
        validation_results = ASLValidator().validate(validation_data)
        combined_major_errors, combined_major_errors_concise, combined_errors, combined_errors_concise, \
        combined_warnings, combined_warnings_concise, combined_values = validation_results

        # Add M0-specific errors and warnings
        ASLUtils.ensure_keys_and_append(combined_errors, "m0_error", context.errors)
        ASLUtils.ensure_keys_and_append(combined_warnings, "m0_warning", context.warnings)

        # Generate concise error and warning texts
        error_texts = self._generate_concise_texts(combined_major_errors_concise, combined_errors_concise, combined_warnings_concise)

        # Extract inconsistencies
        inconsistencies = self._extract_inconsistencies(combined_errors_concise, combined_major_errors_concise, combined_warnings_concise)

        # Generate M0-specific concise errors and warnings
        m0_concise_error, m0_concise_error_params = ASLUtils.condense_and_reformat_discrepancies(context.errors)
        m0_concise_warning, _ = ASLUtils.condense_and_reformat_discrepancies(context.warnings)

        # Determine M0 TR and generate reports
        M0_TR, report_line_on_M0 = ASLUtils.determine_m0_tr_and_report(
            context.m0_prep_times_collection, context.all_absent, context.bs_all_off, 
            context.errors, m0_type=context.m0_type, inconsistent_params=m0_concise_error_params
        )

        # Generate ASL and M0 reports
        reports = self._generate_reports(
            combined_values, combined_major_errors, combined_errors, context, M0_TR, report_line_on_M0
        )

        # Prepare parameters
        parameters = self._prepare_parameters(context, M0_TR, reports)

        required_condition_schema = config['schemas']['required_condition_schema']
        missing_required_parameters = []
        for idx, session in enumerate(context.asl_json_data):
            asl_type = session.get('ArterialSpinLabelingType', None)
            for param, condition in required_condition_schema.items():
                # Determine if this param is required for this ASL type
                is_required = False
                if condition == 'all':
                    is_required = True
                elif isinstance(condition, dict):
                    asl_type_list = condition.get('ArterialSpinLabelingType', [])
                    if isinstance(asl_type_list, str):
                        asl_type_list = [asl_type_list]
                    if asl_type and asl_type in asl_type_list:
                        is_required = True
                if is_required and param not in session:
                    missing_required_parameters.append(param)

        return {
            "major_errors": combined_major_errors,
            "major_errors_concise": combined_major_errors_concise,
            "errors": combined_errors,
            "errors_concise": combined_errors_concise,
            "warnings": combined_warnings,
            "warnings_concise": combined_warnings_concise,
            "basic_report": reports["basic_report"],
            "extended_report": reports["extended_report"],
            "nifti_slice_number": context.nifti_slice_number,
            "major_errors_concise_text": error_texts["major_errors"],
            "errors_concise_text": error_texts["errors"],
            "warnings_concise_text": error_texts["warnings"],
            "inconsistencies": "".join(inconsistencies["errors"]),
            "major_inconsistencies": "".join(inconsistencies["major_errors"]),
            "warning_inconsistencies": "".join(inconsistencies["warnings"]),
            "m0_concise_error": "\n".join(m0_concise_error),
            "m0_concise_warning": "\n".join(m0_concise_warning),
            "asl_parameters": parameters["asl"],
            "m0_parameters": parameters["m0"],
            "extended_parameters": parameters["extended"],
            "missing_required_parameters": missing_required_parameters
        }

    def _generate_concise_texts(self, combined_major_errors_concise: Dict, combined_errors_concise: Dict, combined_warnings_concise: Dict) -> Dict[str, str]:
        """
        Generate concise error and warning texts.
        
        Args:
            combined_major_errors_concise: Concise major errors.
            combined_errors_concise: Concise errors.
            combined_warnings_concise: Concise warnings.
            
        Returns:
            Dictionary containing concise texts.
        """
        return {
            "major_errors": ASLUtils.extract_concise_error(combined_major_errors_concise),
            "errors": ASLUtils.extract_concise_error(combined_errors_concise),
            "warnings": ASLUtils.extract_concise_error(combined_warnings_concise)
        }

    def _extract_inconsistencies(self, combined_errors_concise: Dict, combined_major_errors_concise: Dict, combined_warnings_concise: Dict) -> Dict[str, List[str]]:
        """
        Extract inconsistencies from validation results.
        
        Args:
            combined_errors_concise: Concise errors.
            combined_major_errors_concise: Concise major errors.
            combined_warnings_concise: Concise warnings.
            
        Returns:
            Dictionary containing inconsistency lists.
        """
        return {
            "errors": ReportGenerator.extract_inconsistencies(combined_errors_concise),
            "major_errors": ReportGenerator.extract_inconsistencies(combined_major_errors_concise),
            "warnings": ReportGenerator.extract_inconsistencies(combined_warnings_concise)
        }

    def _generate_reports(self, combined_values: Dict, combined_major_errors: Dict, combined_errors: Dict, 
                         context: ProcessingContext, M0_TR: Any, report_line_on_M0: str) -> Dict[str, Any]:
        """
        Generate ASL and M0 reports.
        
        Args:
            combined_values: Combined validation values.
            combined_major_errors: Combined major errors.
            combined_errors: Combined errors.
            context: Processing context.
            M0_TR: M0 TR value.
            report_line_on_M0: M0 report line.
            
        Returns:
            Dictionary containing basic and extended reports.
        """
        asl_report, asl_parameters = ReportGenerator.generate_asl_report(
            combined_values, combined_major_errors, combined_errors, context.global_pattern, 
            context.m0_type, total_acquired_pairs=context.total_acquired_pairs, 
            slice_number=context.nifti_slice_number
        )
        
        m0_report = ReportGenerator.generate_m0_report(report_line_on_M0, M0_TR)
        basic_report = asl_report + m0_report

        extended_report, extended_parameters = ReportGenerator.generate_extended_report(
            combined_values, combined_major_errors, combined_errors
        )
        extended_report = asl_report + extended_report + m0_report

        return {
            "basic_report": basic_report,
            "extended_report": extended_report,
            "asl_parameters": asl_parameters,
            "extended_parameters": extended_parameters
        }

    def _prepare_parameters(self, context: ProcessingContext, M0_TR: Any, reports: Dict) -> Dict[str, List]:
        """
        Prepare parameter lists for the result.
        
        Args:
            context: Processing context.
            M0_TR: M0 TR value.
            reports: Dictionary containing report parameters.
            
        Returns:
            Dictionary containing parameter lists.
        """
        # Prepare M0 parameters
        m0_parameters = [("M0 Type", context.m0_type)]
        if M0_TR:
            m0_parameters.append(("M0 TR", M0_TR))

        # Convert boolean values to strings for ASL and extended parameters
        asl_parameters = [(key, "True" if isinstance(value, bool) and value else value) 
                         for key, value in reports["asl_parameters"]]
        extended_parameters = [(key, "True" if isinstance(value, bool) and value else value) 
                              for key, value in reports["extended_parameters"]]

        return {
            "asl": asl_parameters,
            "m0": m0_parameters,
            "extended": extended_parameters
        }
