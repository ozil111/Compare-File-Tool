# Repository File Comparison Tool

## Overview

This repository provides a robust file comparison tool that supports various file formats, including text, CSV, JSON, XML, and binary files. The tool offers flexible configuration options and is designed to be used for automated file analysis and validation.

## Features

- **Multi-format comparison**: Supports text, JSON, XML, CSV, and binary files.
- **Line and column selection**: Compare specific ranges within text-based files.
- **Flexible output formats**: Results can be generated in plain text, JSON, or HTML.
- **Customizable JSON key-based comparison**: Enables structured JSON comparisons based on specific keys.
- **Binary file hashing and chunked comparison**: Efficiently detects differences in binary files.
- **Similarity Index for binary files**: When comparing binary files, use the `--similarity` option to compute and display a similarity index based on the formula:  
  **Similarity = 2 * LCS length / (file1 length + file2 length)**
- **Extensible design**: New file formats can be added easily using the factory pattern.

## Installation

This tool requires Python 3.9 or higher. Install the required dependencies using:

```sh
pip install -r requirements.txt
```

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
- `--file-type`: Specify file type (`text`, `json`, `xml`, `csv`, `binary`, `h5`). Default is `auto`.
- `--output-format`: Choose output format (`text`, `json`, `html`).
- `--json-compare-mode`: Specify JSON comparison mode (`exact` or `key-based`).
- `--json-key-field`: Specify key fields for key-based JSON comparison (comma-separated for multiple keys).
- `--verbose`: Enable detailed logs.
- `--similarity`: (Binary files only) Compute and display the similarity index even if the files are not completely identical.
- `--num-threads`: Specify the number of threads for parallel processing (default is 4).
- `--h5-table`: (HDF5 files only) Comma-separated list of table names to compare in HDF5 files.
- `--h5-structure-only`: (HDF5 files only) Only compare HDF5 file structure without comparing content.
- `--h5-show-content-diff`: (HDF5 files only) Show detailed content differences when content differs.
- `--debug`: Enable debug mode with detailed logging.

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

Uses chunked byte-wise comparison and SHA-256 hashing to detect differences. Additionally, with the `--similarity` option, a similarity index is calculated using:

**Similarity = 2 \* LCS length / (file1 length + file2 length)**

### HDF5 Files

Supports comprehensive comparison of HDF5 files with the following features:
- Structure comparison: Compare file structure, including datasets, groups, and attributes
- Content comparison: Compare actual data content with configurable precision
- Selective comparison: Compare specific tables/datasets
- Attribute comparison: Compare metadata and attributes
- Detailed differences: Option to show detailed content differences
- Numerical comparison: Uses numpy.isclose for floating-point comparisons with configurable tolerances

Example HDF5 comparison:
```sh
python compare_text.py file1.h5 file2.h5 \
  --file-type h5 \
  --h5-table dataset1,group1/dataset2 \
  --h5-structure-only \
  --h5-show-content-diff \
  --verbose
```

## Architecture

### Directory Structure

```
Compare-File-Tool/
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

Xiaotong Wang
email: XiaotongWang98@gmail.com