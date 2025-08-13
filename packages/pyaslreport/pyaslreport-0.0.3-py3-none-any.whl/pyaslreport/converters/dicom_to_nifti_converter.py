import json
import os
import re
import subprocess
import tempfile
import pydicom
import dicom2nifti

class DICOM2NiFTIConverter:
    """
    Converts DICOM files to NIfTI format.
    """

    @staticmethod
    def convert(dcm_files, nifti_file=None, converted_files_location="/tmp/upload"):

        """
        Convert DICOM files to NIfTI format.
        """
        converted_files = []
        converted_filenames = []
        nifti_file_assigned = nifti_file
        processed_series = set()
        series_repetitions = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            for dcm_file in dcm_files:

                ds = pydicom.dcmread(dcm_file)
                series_number_tag = ds.get((0x0020, 0x0011), None)

                if series_number_tag:
                    series_number = series_number_tag.value
                    if series_number in processed_series:
                        continue  # Skip processing if this series has already been processed

                    processed_series.add(series_number)

                    # Print the line with "lRepetitions" if present
                    private_0029_1020 = ds.get((0x0029, 0x1020), None)
                    if private_0029_1020:
                        value = private_0029_1020.value.decode('latin1')  # Fallback to another encoding

                        match = re.search(r"lRepetitions\s*=\s*(\d+)", value)
                        if match:
                            lRepetitions_value = match.group(1)
                            series_repetitions[series_number] = lRepetitions_value

            # Check if there are any DICOM files in the temporary directory
            if not os.listdir(temp_dir):
                return None, None, nifti_file, "nifti", "No DICOM files found."

            # Ensure converted_files_location exists
            os.makedirs(converted_files_location, exist_ok=True)

            # Run dcm2niix on the temporary directory with the DICOM files
            try:
                result = subprocess.run(
                    ['dcm2niix', '-z', 'y', '-o', converted_files_location, temp_dir],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                print(result.stdout.decode())
            except subprocess.CalledProcessError as e:
                print(f"Error: {e.stderr.decode()}")
                return None, None, nifti_file, None, e.stderr.decode()

            # Collect the converted files
            for root, dirs, files in os.walk(converted_files_location):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.endswith('.nii') or file.endswith('.nii.gz'):
                        if nifti_file_assigned is None:
                            nifti_file_assigned = file_path
                    elif file.endswith('.json'):
                        with open(file_path, 'r') as json_file:
                            json_data = json.load(json_file)

                        series_number = json_data.get('SeriesNumber', None)
                        if series_number and series_number in series_repetitions:
                            json_data['lRepetitions'] = series_repetitions[series_number]
                            with open(file_path, 'w') as json_file:
                                json.dump(json_data, json_file, indent=4)

                        converted_files.append(file_path)
                        converted_filenames.append(file)
                    else:
                        print(f"Error: Unexpected file format {file_path}")
                        return None, None, nifti_file, None, f"Unexpected file format: {file_path}"

        if nifti_file_assigned is None:
            return None, None, None, "nifti", "No NIfTI file was generated."

        return converted_files, converted_filenames, nifti_file_assigned, "dicom", None


    @staticmethod
    def dir_to_nifti(dicom_dir: str, output_dir: str, bids_basename: str, overwrite: bool = False) -> str:
        """
        Convert a DICOM series to a NIfTI file.
        Returns the path to the NIfTI file.
        """
        os.makedirs(output_dir, exist_ok=True)
        nifti_path = os.path.join(output_dir, f"{bids_basename}.nii.gz")
        if not os.path.exists(nifti_path) or overwrite:
            dicom2nifti.convert_directory(dicom_dir, output_dir, compression=True, reorient=True)
            # Find the generated NIfTI file 
            for f in os.listdir(output_dir):
                if f.endswith('.nii.gz'):
                    os.rename(os.path.join(output_dir, f), nifti_path)
                    break
        return nifti_path