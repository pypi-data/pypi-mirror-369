

class TsvWriter:
    @staticmethod
    def write(data, filepath):
        """
        Write data to a TSV file.
        Args:
            data (list): The data to write to the TSV file.
            filepath (str): The path to the file where the data should be written.
        Raises:
            IOError: If there is an error writing to the file.
        """
        with open(filepath, 'w') as file:
            for row in data:
                file.write('\t'.join(row) + '\n')
            