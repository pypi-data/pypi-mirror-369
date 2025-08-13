import json

class JSONWriter:

    @staticmethod
    def write(data, filepath):
        """
        Write data to a JSON file.
        Args:
            data (dict): The data to write to the JSON file.
            filepath (str): The path to the file where the data should be written.
        Raises:
            IOError: If there is an error writing to the file.
        """
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=2)