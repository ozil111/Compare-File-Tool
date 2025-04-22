import subprocess
import os
import sys
import unittest
from pathlib import Path

class TestFileComparison(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.script_path = os.path.abspath(__file__)
        cls.workspace = os.path.dirname(os.path.dirname(cls.script_path))
        cls.compare_script = os.path.join(cls.workspace, "compare_text.py")
        cls.test_dir = os.path.join(cls.workspace, "test")

    def run_comparison(self, file1, file2, expected_output=None, expected_error=None):
        """Run file comparison and return result"""
        cmd = [
            sys.executable,
            self.compare_script,
            os.path.join("test", file1),
            os.path.join("test", file2)
        ]
        
        result = subprocess.run(
            cmd,
            cwd=self.workspace,
            capture_output=True,
            text=True
        )
        
        full_output = result.stdout + result.stderr
        
        if expected_output:
            self.assertIn(expected_output, full_output)
        if expected_error:
            self.assertIn(expected_error, full_output)
            
        return result.returncode == 0

    def test_identical_bdf_files(self):
        """Test comparison of identical BDF files"""
        self.assertTrue(
            self.run_comparison("1.bdf", "1_copy.bdf", "Files are identical."),
            "Failed to detect identical BDF files"
        )

    def test_different_bdf_files(self):
        """Test comparison of different BDF files"""
        self.assertFalse(
            self.run_comparison("1.bdf", "2.bdf", "Files are different"),
            "Failed to detect different BDF files"
        )

    def test_identical_json_files(self):
        """Test comparison of identical JSON files"""
        self.assertTrue(
            self.run_comparison("1.json", "1_copy.json", "Files are identical."),
            "Failed to detect identical JSON files"
        )

    def test_different_json_files(self):
        """Test comparison of different JSON files"""
        self.assertFalse(
            self.run_comparison("1.json", "2.json", "Files are different"),
            "Failed to detect different JSON files"
        )

    def test_identical_h5_files(self):
        """Test comparison of identical H5 files"""
        self.assertTrue(
            self.run_comparison("1.h5", "1.h5", "Files are identical."),
            "Failed to detect identical H5 files"
        )

    def test_different_h5_files(self):
        """Test comparison of different H5 files"""
        self.assertFalse(
            self.run_comparison("1.h5", "2.h5", "Files are different"),
            "Failed to detect different H5 files"
        )

    def test_nonexistent_file(self):
        """Test handling of nonexistent file"""
        self.assertFalse(
            self.run_comparison("nonexistent.bdf", "1.bdf", 
                              expected_error="File not found"),
            "Failed to handle nonexistent file"
        )

    def test_invalid_file_type(self):
        """Test handling of invalid file type"""
        # Create a temporary invalid file
        invalid_file = os.path.join(self.test_dir, "invalid.xyz")
        with open(invalid_file, "w") as f:
            f.write("test content")
            
        try:
            self.assertFalse(
                self.run_comparison("invalid.xyz", "1.bdf",
                                  expected_error="Unsupported file type"),
                "Failed to handle invalid file type"
            )
        finally:
            # Clean up
            if os.path.exists(invalid_file):
                os.remove(invalid_file)

    def test_empty_files(self):
        """Test comparison of empty files"""
        # Create temporary empty files
        empty1 = os.path.join(self.test_dir, "empty1.txt")
        empty2 = os.path.join(self.test_dir, "empty2.txt")
        
        try:
            with open(empty1, "w") as f1, open(empty2, "w") as f2:
                pass
                
            self.assertTrue(
                self.run_comparison("empty1.txt", "empty2.txt", "Files are identical."),
                "Failed to compare empty files"
            )
        finally:
            # Clean up
            for f in [empty1, empty2]:
                if os.path.exists(f):
                    os.remove(f)

if __name__ == "__main__":
    unittest.main()