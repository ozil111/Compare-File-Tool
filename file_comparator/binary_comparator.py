import hashlib
from .base_comparator import BaseComparator
from .result import Difference
from concurrent.futures import ThreadPoolExecutor

class BinaryComparator(BaseComparator):
    def __init__(self, encoding="utf-8", chunk_size=8192, verbose=False, similarity=False, num_threads=4):
        super().__init__(encoding, chunk_size, verbose)
        self.similarity = similarity
        self.num_threads = num_threads

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
            identical = False
        elif content1 == content2:
            differences = []
            identical = True
        else:
            identical = False
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
        
        return identical, differences

    def compute_lcs_length(self, a: bytes, b: bytes) -> int:
# 利用二维 DP 来计算最长公共子序列 (内存占用优化为一维数组)
        if not a or not b:
            return 0

        def lcs_worker(start, end):
            previous = [0] * (len(b) + 1)
            for i in range(start, end):
                current = [0] * (len(b) + 1)
                for j in range(1, len(b) + 1):
                    if a[i - 1] == b[j - 1]:
                        current[j] = previous[j - 1] + 1
                    else:
                        current[j] = max(previous[j], current[j - 1])
                previous = current
            return previous[len(b)]

        chunk_size = len(a) // self.num_threads
        futures = []

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            for i in range(self.num_threads):
                start = i * chunk_size
                end = (i + 1) * chunk_size if i != self.num_threads - 1 else len(a)
                futures.append(executor.submit(lcs_worker, start, end))

        lcs_length = sum(f.result() for f in futures)
        return lcs_length

    def compare_files(self, file1, file2, start_line=0, end_line=None, start_column=0, end_column=None):
        from pathlib import Path
        from .result import ComparisonResult
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
            file1_path = Path(file1)
            file2_path = Path(file2)
            result.file1_size = file1_path.stat().st_size
            result.file2_size = file2_path.stat().st_size
            self.logger.debug("Reading content from files")
            content1 = self.read_content(file1, start_line, end_line, start_column, end_column)
            content2 = self.read_content(file2, start_line, end_line, start_column, end_column)
            self.logger.debug("Comparing content")
            identical, differences = self.compare_content(content1, content2)
            result.identical = identical
            result.differences = differences
            if self.similarity:
                if (len(content1) + len(content2)) > 0:
                    lcs_len = self.compute_lcs_length(content1, content2)
                    similarity = 2 * lcs_len / (len(content1) + len(content2))
                else:
                    similarity = 1
                result.similarity = similarity
            return result
        except Exception as e:
            self.logger.error(f"Error during comparison: {str(e)}")
            result.error = str(e)
            result.identical = False
            return result

    def get_file_hash(self, file_path, chunk_size=8192):
        """Calculate SHA-256 hash of a file efficiently"""
        h = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                h.update(chunk)
        return h.hexdigest()