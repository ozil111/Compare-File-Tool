# 🔍 Repository File Comparison Tool

A powerful, flexible, and extensible tool to **compare text, CSV, JSON, XML, binary, and HDF5 files** — perfect for automated validation, testing, and data inspection.

------

## ✨ Key Features

- **🧩 Multi-format support**: Compare text, JSON, XML, CSV, binary, and HDF5 files out-of-the-box.
- **🎯 Fine-grained control**: Focus comparisons on specific lines, columns, keys, or HDF5 tables.
- **🛠 Flexible outputs**: Get differences in text, JSON, or beautiful HTML reports.
- **🧠 Smart JSON comparison**: Key-based matching for structured data.
- **⚡️ Fast binary analysis**: Efficient hashing, chunking, and optional similarity scoring.
- **🚀 Easy extensibility**: Add new file types seamlessly using a clean factory pattern.

---

## ❓ Why This Project?

While many existing tools focus on comparing plain text or specific formats like JSON, very few offer a **unified, extensible solution** for **multi-format file comparison**, especially for **structured data formats** like HDF5.
 This project bridges that gap by offering:

- 🚀 **Automation-Ready**: Easily integrated into scripts, pipelines, or automated testing workflows.
- 🧩 **Multi-Format Support**: Seamlessly compare text, CSV, JSON, XML, binary, and HDF5 files in one tool.
- 🎯 **Fine-Grained Control**: Compare specific line ranges, column ranges, or structured fields.
- 🔌 **Extensibility by Design**: Add new formats in minutes using a clean comparator architecture.
- 🛠 **Designed for Engineers and Researchers**: Particularly useful in scientific computing, simulation validation, data engineering, and automated QA processes.

Whether you are validating simulation results, checking large dataset exports, or building continuous integration pipelines, **this tool can save you time and improve reliability**.

------

## 🚀 Quickstart

1. Install Python 3.9+ and dependencies:

```bash
pip install -r requirements.txt
```

1. Compare two files with one command:

```bash
python compare_text.py file1.txt file2.txt
```

1. Need more control? See [Advanced Options](#-advanced-options)!

------

## ⚙️ Usage

### Basic Comparison

```bash
python compare_text.py file1.txt file2.txt
```

### Advanced Options

```bash
python compare_text.py file1.txt file2.txt \
  --start-line 10 --end-line 50 \
  --start-column 5 --end-column 20 \
  --file-type json --output-format json \
  --json-compare-mode key-based --json-key-field id,name \
  --verbose
```

Available parameters:

| Parameter                        | Description                                                  |
| -------------------------------- | ------------------------------------------------------------ |
| `file1`, `file2`                 | Paths to the files to compare                                |
| `--file-type`                    | File type: `text`, `json`, `xml`, `csv`, `binary`, `h5` (default: `auto`) |
| `--start-line`, `--end-line`     | Compare specific line ranges                                 |
| `--start-column`, `--end-column` | Compare specific column ranges                               |
| `--output-format`                | Output format: `text`, `json`, `html`                        |
| `--json-compare-mode`            | JSON comparison: `exact` or `key-based`                      |
| `--json-key-field`               | Key fields for JSON matching                                 |
| `--similarity`                   | (Binary only) Compute similarity index                       |
| `--h5-table`                     | (HDF5 only) Specify tables/datasets                          |
| `--h5-table-regex`               | (HDF5 only) Regular expression pattern to match table names  |
| `--h5-structure-only`            | (HDF5 only) Compare structure only                           |
| `--h5-show-content-diff`         | (HDF5 only) Show detailed differences                        |
| `--h5-rtol`                      | (HDF5 only) Relative tolerance for numerical comparison (default: 1e-5) |
| `--h5-atol`                      | (HDF5 only) Absolute tolerance for numerical comparison (default: 1e-8) |
| `--verbose`, `--debug`           | Enable detailed logs                                         |
| `--num-threads`                  | Parallelism (default: 4)                                     |

------

## 📚 Supported File Types

| Format     | Capabilities                                                 |
| ---------- | ------------------------------------------------------------ |
| **Text**   | Line-by-line and column-based comparison                     |
| **JSON**   | Exact or key-based structured comparison                     |
| **XML**    | Structure, attributes, and content diffing                   |
| **CSV**    | Row-by-row, column-by-column analysis                        |
| **Binary** | Chunked comparison, SHA-256 hashing, similarity index        |
| **HDF5**   | Structure + content comparison, dataset selection, numerical tolerance, regex table matching |

Example HDF5 comparison:

```bash
# Compare specific tables
python compare_text.py file1.h5 file2.h5 \
  --file-type h5 \
  --h5-table dataset1,group1/dataset2 \
  --h5-structure-only \
  --h5-show-content-diff \
  --h5-rtol 1e-4 \
  --h5-atol 1e-6 \
  --verbose

# Compare tables matching a pattern
python compare_text.py file1.h5 file2.h5 \
  --file-type h5 \
  --h5-table-regex "^time.*" \
  --h5-show-content-diff \
  --verbose
```

The HDF5 comparison supports:
- Exact table name matching with `--h5-table`
- Regular expression pattern matching with `--h5-table-regex`
- Structure-only comparison with `--h5-structure-only`
- Detailed content differences with `--h5-show-content-diff`
- Configurable numerical comparison tolerances with `--h5-rtol` and `--h5-atol`

------

## 🏗 Architecture

```bash
Compare-File-Tool/
├── compare_text.py          # Entry script
├── file_comparator/
│   ├── base_comparator.py   # Base class
│   ├── factory.py           # Factory for comparator creation
│   ├── text_comparator.py   # Text file comparison
│   ├── json_comparator.py   # JSON file comparison
│   ├── xml_comparator.py    # XML file comparison
│   ├── csv_comparator.py    # CSV file comparison
│   ├── binary_comparator.py # Binary file comparison
│   ├── h5_comparator.py     # HDF5 file comparison
│   ├── result.py            # Stores and formats results
```

------

## 🔌 Extending the Tool

Want to add support for a new file format?
 Just create a new comparator by extending `BaseComparator` and register it:

```python
from .base_comparator import BaseComparator
class MyFormatComparator(BaseComparator):
    def read_content(self, file_path, ...):
        ...
    def compare_content(self, content1, content2):
        ...
from .factory import ComparatorFactory
ComparatorFactory.register_comparator('myformat', MyFormatComparator)
```

You can have your new format supported in minutes!

---

## 🛣 Future Plans

We are committed to continuously improving this project. Planned enhancements include:

- 📦 **Python API**: Allow programmatic usage (`compare_files(file1, file2)`) without command-line execution.
- 🧪 **Better Testing Integration**: Provide `pytest` plugins and examples for easier integration into CI/CD pipelines.
- 📈 **Performance Optimization**: Explore faster comparison algorithms for large binary and HDF5 files.
- 🌐 **Docker Image**: Offer a pre-built Docker image for easy setup across platforms.
- 🎨 **More Output Formats**: Add Markdown and rich diff view formats for better human readability.
- 🚀 **PyPI Release**: Package and publish the tool to PyPI for easier installation via `pip install compare-file-tool`.
- ✍️ **More Real-World Examples**: Share practical use cases (e.g., validating ML model outputs, database migration verification).
- 🌍 **Community Contributions**: Open issues and ideas for contributors to extend format support and improve user experience.

------

## 📜 License

This project is licensed under the **MIT License** — free for personal and commercial use.

------

## 🙋‍♂️ Contact

Questions? Ideas?
 Feel free to open an issue or a pull request.

**Author**: Xiaotong Wang
 **Email**: XiaotongWang98@gmail.com

------

# 🔥 Why Choose This Tool?

- ✅ Clean and extensible codebase
- ✅ Rich options for precise comparison
- ✅ Supports modern data formats like HDF5
- ✅ Battle-tested for validation and testing workflows