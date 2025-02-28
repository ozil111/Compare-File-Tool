import hashlib
from .base_comparator import BaseComparator
from .result import Difference

class BinaryComparator(BaseComparator):
    """Comparator for binary files with chunk-by-chunk comparison"""
    
    def read_content(self, file_path, start_line=0, end_line=None, start_column=0, end_column=None):
        """
        Read binary content. For binary files, the parameters are interpreted as:
        start_line: starting byte offset
        end_line: ending byte offset
        start_column/end_column: ignored for binary files
        """
        try:
            self.logger.debug(f"Reading binary file: {file_path}")
            
            # For binary files, interpret start_line as byte offset
            start_offset = start_line
            end_offset = end_line
            
            with open(file_path, 'rb') as f:
                if start_offset > 0:
                    f.seek(start_offset)
                
                if end_offset is not None:
                    if end_offset <= start_offset:
                        raise ValueError("End offset must be greater than start offset")
                    bytes_to_read = end_offset - start_offset
                    content = f.read(bytes_to_read)
                else:
                    content = f.read()
                    
            return content
                
        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except IOError as e:
            raise ValueError(f"Error reading file {file_path}: {str(e)}")
    
    def compare_content(self, content1, content2):
        """Compare binary content efficiently"""
        self.logger.debug(f"Comparing binary content")
        
        if len(content1) != len(content2):
            differences = [Difference(
                position="file size",
                expected=f"{len(content1)} bytes",
                actual=f"{len(content2)} bytes",
                diff_type="size"
            )]
            return False, differences
            
        if content1 == content2:
            return True, []
        
        # Find the differences
        differences = []
        offset = 0
        max_differences = 10  # Limit number of differences reported
        
        for i in range(0, len(content1), self.chunk_size):
            chunk1 = content1[i:i+self.chunk_size]
            chunk2 = content2[i:i+self.chunk_size]
            
            if chunk1 != chunk2:
                # Find the exact byte position where the difference starts
                for j in range(len(chunk1)):
                    if j >= len(chunk2) or chunk1[j] != chunk2[j]:
                        diff_pos = i + j
                        # Show a few bytes before and after the difference for context
                        context_size = 8
                        start_ctx = max(0, diff_pos - context_size)
                        end_ctx = min(len(content1), diff_pos + context_size)
                        
                        # Create hex representations of the differing sections
                        expected_bytes = content1[start_ctx:end_ctx]
                        actual_bytes = content2[start_ctx:min(len(content2), end_ctx)]
                        
                        expected_hex = ' '.join(f"{b:02x}" for b in expected_bytes)
                        actual_hex = ' '.join(f"{b:02x}" for b in actual_bytes)
                        
                        differences.append(Difference(
                            position=f"byte {diff_pos}",
                            expected=expected_hex,
                            actual=actual_hex,
                            diff_type="content"
                        ))
                        break
                        
                if len(differences) >= max_differences:
                    differences.append(Difference(
                        position=None,
                        expected=None,
                        actual=None,
                        diff_type=f"more differences not shown"
                    ))
                    break
        
        return False, differences
    
    def get_file_hash(self, file_path, chunk_size=8192):
        """Calculate SHA-256 hash of a file efficiently"""
        h = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                h.update(chunk)
        return h.hexdigest()