import argparse
from pyaslreport import generate_report


def main():
    """
    Command-line interface for generating a report from ASL files.
    This script uses argparse to parse command-line arguments and calls the
    generate_report function from the pyaslreport module.
    Usage:
    python generate_report.py --modality asl --files file1 file2 --filenames filename1 filename2 --nifti_file path/to/nifti_file.nii --dcm_files dcm_file1 dcm_file2
    """
    parser = argparse.ArgumentParser(description="Generate report from ASL files.")

    parser.add_argument('--modality', required=True, help="Modality (e.g., asl)")
    parser.add_argument('--files', nargs='+', required=True, help="List of file paths")
    parser.add_argument('--filenames', nargs='+', required=True, help="List of filenames")
    parser.add_argument('--nifti_file', required=True, help="Path to NIfTI file")
    parser.add_argument('--dcm_files', nargs='*', default=[], help="List of DICOM files (optional)")

    args = parser.parse_args()

    data = {
        "modality": args.modality,
        "files": args.files,
        "filenames": args.filenames,
        "nifti_file": args.nifti_file,
        "dcm_files": args.dcm_files
    }

    generate_report(data)


if __name__ == "__main__":
    main()
