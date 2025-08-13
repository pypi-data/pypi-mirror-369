import nibabel as nib

class NiftiReader:

    @staticmethod
    def read(nifti_file):
        """
        Reads a NIfTI file and returns the NIfTI image object.
        Args:
            nifti_file (str): Path to the NIfTI file to be read.
        Returns:
            nib.Nifti1Image: NIfTI image object if the file is valid.
        """
        try:
            if isinstance(nifti_file, str):
                if not nifti_file.endswith(('.nii', '.nii.gz')):
                    raise ValueError("File must be a NIfTI file with .nii or .nii.gz extension.")

                nifti_filepath = nifti_file

            else:
                raise ValueError("Unsupported file type. Expected a string path to a NIfTI file.")

            nifti_img = nib.load(nifti_filepath)
            return nifti_img

        except Exception as e:
            raise RuntimeError(f"Error reading NIfTI file: {str(e)}") from e
