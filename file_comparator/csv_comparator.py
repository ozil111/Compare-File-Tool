import csv
import io
from .text_comparator import TextComparator
from .result import Difference

class CsvComparator(TextComparator):
    """Comparator for CSV files with row and column comparison"""
    
    def __init__(self, encoding="utf-8", delimiter=",", quotechar='"', chunk_size=8192, verbose=False):
        super().__init__(encoding, chunk_size, verbose)
        self.delimiter = delimiter
        self.quotechar = quotechar
    
    def read_content(self, file_path, start_line=0, end_line=None, start_column=0, end_column=None):
        """Read CSV content"""
        # First read the file as text
        text_content = super().read_content(file_path, start_line, end_line, start_column, end_column)
        
        # Join the lines to create a CSV string
        csv_text = ''.join(text_content)
        
        # Parse the CSV
        csv_data = []
        csv_reader = csv.reader(
            io.StringIO(csv_text), 
            delimiter=self.delimiter,
            quotechar=self.quotechar
        )
        
        for row in csv_reader:
            # Apply column range if specified
            if start_column > 0 or end_column is not None:
                col_start = start_column
                col_end = end_column if end_column is not None else len(row)
                row = row[col_start:col_end+1]
            csv_data.append(row)
            
        return csv_data
    
    def compare_content(self, content1, content2):
        """Compare CSV content"""
        if content1 == content2:
            return True, []
            
        differences = []
        
        # Check row count
        if len(content1) != len(content2):
            differences.append(Difference(
                position="row count",
                expected=f"{len(content1)} rows",
                actual=f"{len(content2)} rows",
                diff_type="row_count_mismatch"
            ))
        
        # Compare rows
        max_diffs = 10
        for i, (row1, row2) in enumerate(zip(content1, content2)):
            # Check column count in this row
            if len(row1) != len(row2):
                differences.append(Difference(
                    position=f"row {i+1}",
                    expected=f"{len(row1)} columns",
                    actual=f"{len(row2)} columns",
                    diff_type="column_count_mismatch"
                ))
                if len(differences) >= max_diffs:
                    break
            
            # Compare column values
            for j, (cell1, cell2) in enumerate(zip(row1, row2)):
                if cell1 != cell2:
                    differences.append(Difference(
                        position=f"row {i+1}, column {j+1}",
                        expected=cell1,
                        actual=cell2,
                        diff_type="cell_mismatch"
                    ))
                    if len(differences) >= max_diffs:
                        break
            
            if len(differences) >= max_diffs:
                break
        
        # Add a summary if there are more differences
        if len(differences) >= max_diffs:
            differences.append(Difference(
                position=None,
                expected=None,
                actual=None,
                diff_type=f"more differences not shown"
            ))
        
        return False, differences