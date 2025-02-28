from abc import ABC, abstractmethod
import logging
from pathlib import Path
from .result import ComparisonResult, Difference

class BaseComparator(ABC):
    """Base abstract class for all file comparators"""
    
    def __init__(self, encoding="utf-8", chunk_size=8192, verbose=False):
        self.encoding = encoding
        self.chunk_size = chunk_size
        self.logger = logging.getLogger(f"file_comparator.{self.__class__.__name__}")
        if verbose:
            self.logger.setLevel(logging.DEBUG)
    
    @abstractmethod
    def read_content(self, file_path, start_line=0, end_line=None, start_column=0, end_column=None):
        """Read file content with specified range"""
        pass

    @abstractmethod
    def compare_content(self, content1, content2):
        """Compare two content objects and return comparison details"""
        pass

    def compare_files(self, file1, file2, start_line=0, end_line=None, start_column=0, end_column=None):
        """Compare two files with the specified parameters"""
        result = ComparisonResult(
            file1=str(file1),
            file2=str(file2),
            start_line=start_line,
            end_line=end_line,
            start_column=start_column,
            end_column=end_column
        )
        
        try:
            self.logger.info(f"Comparing files: {file1} and {file2}")
            
            # Record file metadata
            file1_path = Path(file1)
            file2_path = Path(file2)
            result.file1_size = file1_path.stat().st_size
            result.file2_size = file2_path.stat().st_size
            
            # Read content with specified ranges
            self.logger.debug(f"Reading content from files")
            content1 = self.read_content(file1, start_line, end_line, start_column, end_column)
            content2 = self.read_content(file2, start_line, end_line, start_column, end_column)
            
            # Compare content
            self.logger.debug(f"Comparing content")
            identical, differences = self.compare_content(content1, content2)
            
            # Update result
            result.identical = identical
            result.differences = differences
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during comparison: {str(e)}")
            result.error = str(e)
            result.identical = False
            return result