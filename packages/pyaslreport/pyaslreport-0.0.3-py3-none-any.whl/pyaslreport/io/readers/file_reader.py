import json


class FileReader:

    @staticmethod
    def read(file_path):
        """
        Reads a file and returns its content based on the file type.
        Supported file types are JSON and TSV. If the file is empty, it returns None.
        Args:
            file_path (str): Path to the file to be read.
        Returns:
            Parsed content of the file.
        """
        try:
            file_stream = open(file_path, 'r')
            if file_path.endswith('.json'):
                return FileReader._read_json(file_stream)

            elif file_path.endswith('.tsv'):
                return FileReader._read_tsv(file_stream)

            else:
                raise RuntimeError("Unsupported file format")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error decoding JSON from file: {e.msg}")
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error reading file: {str(e)}")

    @staticmethod
    def _read_json(file_stream):
        """
        Reads a JSON file and returns its content.

        Args:
         file_stream (file object): File stream of the JSON file to be read.
        Returns:
             Parsed JSON data.
        """
        with file_stream as f:
            content = f.read().strip()  # Read the content and strip any leading/trailing whitespace
            if content:  # Check if the file is not empty
                data = json.loads(content)
                return data
            else:
                return None

    @staticmethod
    def _read_tsv(file_stream):
        """
        Reads a TSV file and returns its content as a list of strings.
        Args: file_stream (file object): File stream of the TSV file to be read.
        Returns:
         List of strings representing the TSV content, or None if the file is empty.
        """
        with file_stream as f:
            lines = f.readlines()

        if not lines:
            return None

        header = lines[0].strip()

        if header != 'volume_type':
            raise RuntimeError("Invalid TSV header, not \"volume_type\"")

        data = [line.strip() for line in lines[1:]]
        return data
