import sys
import os
import argparse
import logging
from pathlib import Path
from file_comparator.factory import ComparatorFactory
from file_comparator.result import ComparisonResult

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("file_comparator")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Compare two files.")
    parser.add_argument("file1", help="Path to the first file")
    parser.add_argument("file2", help="Path to the second file")
    parser.add_argument("--start-line", type=int, default=1, help="Starting line number (1-based)")
    parser.add_argument("--end-line", type=int, help="Ending line number (1-based)")
    parser.add_argument("--start-column", type=int, default=1, help="Starting column number (1-based)")
    parser.add_argument("--end-column", type=int, help="Ending column number (1-based)")
    parser.add_argument("--file-type", help="Type of the files to compare", default="auto")
    parser.add_argument("--encoding", default="utf-8", help="File encoding for text files")
    parser.add_argument("--chunk-size", type=int, default=8192, help="Chunk size for binary comparison")
    parser.add_argument("--output-format", choices=["text", "json", "html"], default="text",
                        help="Output format for the comparison result")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    # Add JSON-specific comparison options
    json_group = parser.add_argument_group('JSON comparison options')
    json_group.add_argument("--json-compare-mode", choices=["exact", "key-based"], default="exact",
                      help="JSON comparison mode: exact (default) or key-based")
    json_group.add_argument("--json-key-field", help="Key field(s) to use for key-based JSON comparison (comma-separated for compound keys)")
    
    return parser.parse_args()

def main():
    logger = configure_logging()

    try:
        args = parse_arguments()

        # Adjust for 0-based indexing
        start_line = max(0, args.start_line - 1)
        end_line = None if args.end_line is None else max(0, args.end_line - 1)
        start_column = max(0, args.start_column - 1)
        end_column = None if args.end_column is None else max(0, args.end_column - 1)

        # Resolve file paths
        file1_path = Path(args.file1).resolve()
        file2_path = Path(args.file2).resolve()

        # Check if files exist
        if not file1_path.exists():
            raise ValueError(f"File not found: {file1_path}")
        if not file2_path.exists():
            raise ValueError(f"File not found: {file2_path}")

        # Determine file type
        file_type = args.file_type
        if file_type == "auto":
            # Auto-detect file type based on extension
            file_type = detect_file_type(file1_path)
            logger.info(f"Auto-detected file type: {file_type}")

        # Create comparator instance
        comparator_kwargs = {
            "encoding": args.encoding,
            "chunk_size": args.chunk_size,
            "verbose": args.verbose
        }
        
        # Add JSON-specific options if applicable
        if file_type == "json" and args.json_compare_mode:
            comparator_kwargs["compare_mode"] = args.json_compare_mode
            if args.json_key_field:
                # Handle comma-separated key fields for compound keys
                key_fields = [field.strip() for field in args.json_key_field.split(',')]
                comparator_kwargs["key_field"] = key_fields[0] if len(key_fields) == 1 else key_fields
                logger.info(f"Using key field(s): {comparator_kwargs['key_field']} for JSON comparison")
        
        comparator = ComparatorFactory.create_comparator(
            file_type,
            **comparator_kwargs
        )

        # Perform the comparison
        result = comparator.compare_files(
            file1_path,
            file2_path,
            start_line,
            end_line,
            start_column,
            end_column
        )

        # Format and output the result
        output = format_result(result, args.output_format)
        print(output)

        # Exit with appropriate status code
        sys.exit(0 if result.identical else 1)

    except ValueError as ve:
        logger.error(f"ValueError: {ve}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"An unexpected error occurred")
        sys.exit(1)

def detect_file_type(file_path):
    # Auto-detect file type based on extension
    extension = file_path.suffix.lower()

    if extension in ['.txt', '.md', '.py', '.java', '.c', '.cpp', '.h', '.js', '.html', '.css', '.bdf', '.f06']:
        return 'text'
    elif extension in ['.json']:
        return 'json'
    elif extension in ['.xml', '.html']:
        return 'xml'
    elif extension in ['.csv']:
        return 'csv'
    else:
        # Default to binary comparison for unknown extensions
        return 'binary'

def format_result(result, output_format):
    # Format the comparison result according to the requested output format
    if output_format == "json":
        import json
        return json.dumps(result.to_dict(), indent=2)
    elif output_format == "html":
        return result.to_html()
    else:
        return str(result)

if __name__ == "__main__":
    main()