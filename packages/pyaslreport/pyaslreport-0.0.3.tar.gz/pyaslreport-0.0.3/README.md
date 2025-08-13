# pyaslreport

A Python package for generating methods sections and reports for ASL (Arterial Spin Labeling) parameters and other medical imaging modalities.

## Overview

`pyaslreport` is a specialized Python library designed to process and analyze medical imaging data, particularly 'for now' ASL (Arterial Spin Labeling) sequences. It provides comprehensive validation, processing, and report generation capabilities for asl publications.

## Features

- **Comprehensive Validation**: Validates ASL parameters, M0 data, and TSV files
- **Report Generation**: Generates detailed reports with errors, warnings, and parameter summaries
- **Extensible Architecture**: Easy to add new modalities and validators

## Installation

### Prerequisites

- Python 3.7 or higher
- pip

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd ASL\ Generator/package

# Install in development mode
pip install -e .
```

### Dependencies

The package automatically installs the following dependencies:
- `PyYAML~=6.0.2` - YAML file processing
- `numpy~=2.2.6` - Numerical computing
- `nibabel~=5.3.2` - Neuroimaging file I/O
- `pydicom~=3.0.1` - DICOM file processing

## Quick Start

### Basic Usage

```python
from pyaslreport import generate_report

# Prepare your data
data = {
    "modality": "asl",
    "files": ["path/to/asl.json", "path/to/m0scan.json", "path/to/data.tsv"],
    "nifti_file": "path/to/asl.nii",
    "dcm_files": ["path/to/dicom1.dcm", "path/to/dicom2.dcm"]  # Optional
}

# Generate report
result = generate_report(data)
print(result)
```

### Command Line Interface

```bash
python -m pyaslreport.cli.generate_report \
    --modality asl \
    --files asl.json m0scan.json data.tsv \
    --filenames asl.json m0scan.json data.tsv \
    --nifti_file image.nii \
    --dcm_files dicom1.dcm dicom2.dcm
```

## Supported Modalities

### ASL (Arterial Spin Labeling)

The ASL processor provides comprehensive analysis of ASL sequences including:

- **Parameter Validation**: Validates ASL-specific parameters like labeling duration, post-labeling delay, etc.
- **M0 Data Analysis**: Processes and validates M0 reference scans
- **TSV File Processing**: Analyzes volume types and timing information
- **Error Detection**: Identifies major errors, minor errors, and warnings

## Input Data Format

### Required Files

- **ASL JSON**: Contains ASL sequence parameters
- **NIfTI File**: The actual imaging data
- **TSV File**: Volume type information and timing data

### Optional Files

- **DICOM Files**: Can be converted to NIfTI format automatically
- **M0 JSON**: M0 reference scan parameters

### Data Structure

```python
{
    "modality": "asl",                    # Required: Modality type
    "files": ["file1.json", "file2.tsv"], # Required: List of file paths
    "nifti_file": "image.nii",            # Required: NIfTI file path
    "dcm_files": ["dcm1.dcm", "dcm2.dcm"] # Optional: DICOM files
}
```

## Output Format

The package returns a comprehensive dictionary containing:

```python
{
    "report": {
        "basic_report": {...},      # Basic parameter summary
        "extended_report": {...},   # Detailed analysis
        "errors": {...},            # Error information
        "warnings": {...}           # Warning information
    },
    "parameters": {} # Extracted ASL parameters
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- **Ibrahim Abdelazim** - [ibrahim.abdelazim@fau.de](mailto:ibrahim.abdelazim@fau.de)
- **Hanliang Xu** - [hxu110@jh.edu](mailto:hxu110@jh.edu)
