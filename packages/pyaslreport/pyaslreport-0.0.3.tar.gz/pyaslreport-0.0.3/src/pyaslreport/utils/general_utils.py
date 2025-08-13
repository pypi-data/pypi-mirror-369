import os
import shutil


class GeneralUtils:

    @staticmethod
    def clean_up_folder(folder_path: str):
        """
        Clean up a folder by deleting all files and subdirectories within it.
        This method will raise an error if it fails to delete any file or directory.
        Args:
            folder_path (str): The path to the folder to be cleaned up.
        """

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                raise RuntimeError(f"Failed to delete {file_path}. Reason: {e}")
