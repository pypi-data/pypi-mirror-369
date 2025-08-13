
class ReportWriter:

    @staticmethod
    def write(report, filepath):
        """
        Write a report to a text file.
        Args:
            report (str): The report content to write to the file.
            filepath (str): The path to the file where the report should be written.
        Raises:
            IOError: If there is an error writing to the file.
        """
        with open(filepath, 'w') as file:
            file.write(report)