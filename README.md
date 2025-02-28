# Repository File Comparison Tool

## Overview

This repository provides a robust file comparison tool that supports various file formats, including text, CSV, JSON, XML, and binary files. The tool offers flexible configuration options and is designed to be used for automated file analysis and validation.

## Features

- **Multi-format comparison**: Supports text, JSON, XML, CSV, and binary files.
- **Line and column selection**: Compare specific ranges within text-based files.
- **Flexible output formats**: Results can be generated in plain text, JSON, or HTML.
- **Customizable JSON key-based comparison**: Enables structured JSON comparisons based on specific keys.
- **Binary file hashing and chunked comparison**: Efficiently detects differences in binary files.
- **Extensible design**: New file formats can be added easily using the factory pattern.

## Installation

This tool requires Python 3.6 or higher. No required dependencies. 

## Usage

### Basic File Comparison

Run the following command to compare two files:

```sh
python compare_text.py file1.txt file2.txt
```

### Advanced Options

```sh
python compare_text.py file1.txt file2.txt \
  --start-line 10 --end-line 50 \
  --start-column 5 --end-column 20 \
  --file-type json --output-format json \
  --json-compare-mode key-based --json-key-field id,name \
  --verbose
```

#### Parameters:

- `file1` and `file2`: Paths to the files to compare.
- `--start-line` and `--end-line`: Limit comparison to specific line ranges.
- `--start-column` and `--end-column`: Limit comparison to specific column ranges.
- `--file-type`: Specify file type (`text`, `json`, `xml`, `csv`, `binary`). Default is `auto`.
- `--output-format`: Choose output format (`text`, `json`, `html`).
- `--json-compare-mode`: Specify JSON comparison mode (`exact` or `key-based`).
- `--json-key-field`: Specify key fields for key-based JSON comparison (comma-separated for multiple keys).
- `--verbose`: Enable detailed logs.

## File Types Supported

### Text Files

Compares content using line-by-line and column-based differences.

### JSON Files

Supports exact and key-based comparison, detecting missing or extra keys.

### XML Files

Parses XML trees and identifies differences in structure, attributes, and content.

### CSV Files

Compares row-by-row, detecting mismatched columns or values.

### Binary Files

Uses chunked byte-wise comparison and SHA-256 hashing to detect differences.

## Architecture

### Directory Structure

```
文件比较/
├── compare_text.py      # Main script for file comparison
├── file_comparator/
│   ├── base_comparator.py      # Abstract base class for all comparators
│   ├── binary_comparator.py    # Comparator for binary files
│   ├── csv_comparator.py       # Comparator for CSV files
│   ├── factory.py              # Comparator factory for dynamic loading
│   ├── h5_comparator.py        # Comparator for HDF5 files
│   ├── json_comparator.py      # Comparator for JSON files
│   ├── result.py               # Stores comparison results and differences
│   ├── text_comparator.py      # Comparator for plain text files
│   ├── xml_comparator.py       # Comparator for XML files
```

## Extending the Tool

To add a new file format, create a new comparator class by inheriting from `BaseComparator` and register it in `factory.py`:

```python
from .base_comparator import BaseComparator
class MyFormatComparator(BaseComparator):
    def read_content(self, file_path, ...):
        pass
    def compare_content(self, content1, content2):
        pass
from .factory import ComparatorFactory
ComparatorFactory.register_comparator('myformat', MyFormatComparator)
```

## License

This project is licensed under the MIT License.

## Contact

For issues or contributions, please open an issue or submit a pull request.
