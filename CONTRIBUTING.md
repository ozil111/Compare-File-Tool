# Contributing to Repository File Comparison Tool

## Overview

Thank you for your interest in contributing to the Repository File Comparison Tool! This document provides guidelines and instructions for contributing to this project.

## Code Style

This project follows a consistent code style to maintain readability and maintainability:

- **Indentation**: Use 4 spaces for indentation (not tabs)
- **Line Length**: Keep lines under 100 characters when possible
- **Naming Conventions**:
  - Class names: PascalCase (e.g., `TextComparator`)
  - Method and variable names: snake_case (e.g., `compare_content`)
  - Constants: UPPER_CASE (e.g., `MAX_DIFFERENCES`)
- **Comments**: Use docstrings for classes and methods, and inline comments for complex logic
- **Type Hints**: Use type hints for function parameters and return values when possible

## Project Structure

The project follows a modular architecture with the following structure:

```
Compare-File-Tool/
├── compare_text.py      # Main script for file comparison
├── file_comparator/     # Core comparison logic
│   ├── base_comparator.py      # Abstract base class
│   ├── binary_comparator.py    # Binary file comparator
│   ├── csv_comparator.py       # CSV file comparator
│   ├── factory.py              # Comparator factory
│   ├── h5_comparator.py        # HDF5 file comparator
│   ├── json_comparator.py      # JSON file comparator
│   ├── result.py               # Comparison results
│   ├── text_comparator.py      # Text file comparator
│   ├── xml_comparator.py       # XML file comparator
├── test_script/         # Testing framework
│   ├── test_cases.json  # Test case definitions
│   ├── test_runner.py   # Test execution engine
```

## Development Workflow

1. **Fork the Repository**: Create your own fork of the repository
2. **Create a Branch**: Create a feature branch for your changes
   ```
   git checkout -b feature/your-feature-name
   ```
3. **Make Changes**: Implement your changes following the code style guidelines
4. **Run Tests**: Ensure all tests pass before submitting your changes
   ```
   python test_script/test_runner.py
   ```
5. **Commit Changes**: Commit your changes with a descriptive message
   ```
   git commit -m "Add feature: description of changes"
   ```
6. **Push to Fork**: Push your changes to your fork
   ```
   git push origin feature/your-feature-name
   ```
7. **Create Pull Request**: Submit a pull request from your fork to the main repository

## Adding New File Format Support

To add support for a new file format:

1. Create a new comparator class in the `file_comparator` directory
2. Inherit from `BaseComparator` and implement the required methods:
   - `read_content`: Parse the file content
   - `compare_content`: Compare the parsed content
3. Register the comparator in `factory.py`
4. Add test cases in `test_cases.json`
5. Update documentation in `README.md`

Example:

```python
from .base_comparator import BaseComparator
from .result import Difference

class MyFormatComparator(BaseComparator):
    def read_content(self, file_path, start_line=0, end_line=None, start_column=0, end_column=None):
        # Implementation for reading the file
        pass
        
    def compare_content(self, content1, content2):
        # Implementation for comparing content
        pass

# Register in factory.py
from .factory import ComparatorFactory
ComparatorFactory.register_comparator('myformat', MyFormatComparator)
```

## Testing Guidelines

- Add test cases for all new features
- Ensure existing tests pass before submitting changes
- Test edge cases and error conditions
- Add tests for different file sizes and formats

## Documentation

- Update the README.md for new features or significant changes
- Add docstrings to new classes and methods
- Include examples for new functionality
- Document any new command-line arguments

## Pull Request Process

1. Ensure your code follows the project's style guidelines
2. Include tests for new functionality
3. Update documentation as needed
4. Provide a clear description of the changes in the pull request
5. Reference any related issues in the pull request description

## Reporting Issues

When reporting issues, please include:

- A clear description of the problem
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Environment details (OS, Python version, etc.)
- Sample files that demonstrate the issue (if applicable)

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License. 