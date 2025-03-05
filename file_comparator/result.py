class Difference:
    """Represents a single difference between files"""
    
    def __init__(self, position=None, expected=None, actual=None, diff_type="content"):
        self.position = position  # Can be line number, byte position, etc.
        self.expected = expected  # Expected content
        self.actual = actual      # Actual content
        self.diff_type = diff_type  # Type of difference: "content", "missing", "extra", etc.
    
    def __str__(self):
        if self.diff_type == "content":
            return f"At {self.position}: expected '{self.expected}', got '{self.actual}'"
        elif self.diff_type == "missing":
            return f"Missing content at {self.position}: '{self.expected}'"
        elif self.diff_type == "extra":
            return f"Extra content at {self.position}: '{self.actual}'"
        else:
            return f"Difference at {self.position}"
    
    def to_dict(self):
        return {
            "position": self.position,
            "expected": self.expected,
            "actual": self.actual,
            "diff_type": self.diff_type
        }

class ComparisonResult:
    """Represents the result of a file comparison"""
    
    def __init__(self, file1=None, file2=None, start_line=0, end_line=None, 
                 start_column=0, end_column=None):
        self.file1 = file1
        self.file2 = file2
        self.file1_size = None
        self.file2_size = None
        self.start_line = start_line
        self.end_line = end_line
        self.start_column = start_column
        self.end_column = end_column
        self.identical = None
        self.differences = []
        self.error = None
        self.similarity = None  # 新增相似度属性
    
    def __str__(self):
        if self.error:
            return f"Error during comparison: {self.error}"
        lines = []
        if self.identical:
            range_str = self._get_range_str()
            lines.append(f"Files are identical{range_str}.")
        else:
            lines.append(f"Files are different. Found {len(self.differences)} differences:")
            for i, diff in enumerate(self.differences, 1):
                lines.append(f"{i}. {diff}")
            if self.similarity is not None:
                lines.append(f"Similarity Index: {self.similarity:.2f}")
        return "\n".join(lines)
    
    def _get_range_str(self):
        parts = []
        if self.start_line > 0 or self.end_line is not None:
            line_range = f"lines {self.start_line+1}"
            if self.end_line is not None:
                line_range += f"-{self.end_line+1}"
            parts.append(line_range)
            
        if self.start_column > 0 or self.end_column is not None:
            col_range = f"columns {self.start_column+1}"
            if self.end_column is not None:
                col_range += f"-{self.end_column+1}"
            parts.append(col_range)
            
        if parts:
            return " in " + ", ".join(parts)
        return ""
    
    def to_dict(self):
        return {
            "file1": self.file1,
            "file2": self.file2,
            "file1_size": self.file1_size,
            "file2_size": self.file2_size,
            "range": {
                "start_line": self.start_line,
                "end_line": self.end_line,
                "start_column": self.start_column,
                "end_column": self.end_column
            },
            "identical": self.identical,
            "differences": [diff.to_dict() for diff in self.differences],
            "similarity": self.similarity,
            "error": self.error
        }
    
    def to_html(self):
        """Convert the result to HTML format"""
        if self.error:
            return f"<div class='error'>Error during comparison: {self.error}</div>"
            
        html = ["<html><head><style>",
                "body { font-family: Arial, sans-serif; }",
                ".identical { color: green; }",
                ".different { color: red; }",
                ".diff-item { margin: 10px 0; padding: 5px; border: 1px solid #ccc; }",
                "</style></head><body>"]
        
        if self.identical:
            range_str = self._get_range_str()
            html.append(f"<h2 class='identical'>Files are identical{range_str}.</h2>")
        else:
            html.append(f"<h2 class='different'>Files are different. Found {len(self.differences)} differences:</h2>")
            if self.similarity is not None:
                html.append(f"<p>Similarity Index: {self.similarity:.2f}</p>")
            html.append("<div class='diff-list'>")
            
            for i, diff in enumerate(self.differences, 1):
                html.append(f"<div class='diff-item'>")
                html.append(f"<h3>Difference {i}</h3>")
                html.append(f"<p>Position: {diff.position}</p>")
                html.append(f"<p>Expected: <pre>{diff.expected}</pre></p>")
                html.append(f"<p>Actual: <pre>{diff.actual}</pre></p>")
                html.append(f"<p>Type: {diff.diff_type}</p>")
                html.append("</div>")
                
            html.append("</div>")
            
        html.append("</body></html>")
        return "\n".join(html)