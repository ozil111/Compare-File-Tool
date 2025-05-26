#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@file compare_text.py
@brief Main script for comparing two files with various comparison methods
@author Xiaotong Wang
@date 2025
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from file_comparator.factory import ComparatorFactory
from file_comparator.result import ComparisonResult

def configure_logging():
    """
    @brief Configure logging settings for the application
    @details Sets up a logger with console handler and formatter
    @return logging.Logger: Configured logger instance
    """
    logger = logging.getLogger("file_comparator")
    logger.setLevel(logging.INFO)
    
    # Create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Add formatter to ch
    ch.setFormatter(formatter)
    
    # Add ch to logger
    logger.addHandler(ch)
    
    return logger

def parse_arguments():
    """
    @brief Parse command line arguments
    @details Sets up argument parser with all necessary options for file comparison
    @return argparse.Namespace: Parsed command line arguments
    """
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
    parser.add_argument("--debug", action="store_true", help="Enable debug mode with detailed logging")
    parser.add_argument("--similarity", action="store_true",
                        help="When comparing binary files, compute and show similarity index")
    parser.add_argument("--num-threads", type=int, default=4, help="Number of threads for parallel processing")
    
    # Add JSON-specific comparison options
    json_group = parser.add_argument_group('JSON comparison options')
    json_group.add_argument("--json-compare-mode", choices=["exact", "key-based"], default="exact",
                      help="JSON comparison mode: exact (default) or key-based")
    json_group.add_argument("--json-key-field", help="Key field(s) to use for key-based JSON comparison (comma-separated for compound keys)")
    
    # Add H5-specific comparison options
    h5_group = parser.add_argument_group('HDF5 comparison options')
    h5_group.add_argument("--h5-table", help="Comma-separated list of table names to compare in HDF5 files")
    h5_group.add_argument("--h5-table-regex", help="Regular expression pattern to match table names in HDF5 files")
    h5_group.add_argument("--h5-structure-only", action="store_true", 
                         help="Only compare HDF5 file structure without comparing content")
    h5_group.add_argument("--h5-show-content-diff", action="store_true",
                         help="Show detailed content differences when content differs")
    h5_group.add_argument("--h5-rtol", type=float, default=1e-5,
                         help="Relative tolerance for numerical comparison in HDF5 files")
    h5_group.add_argument("--h5-atol", type=float, default=1e-8,
                         help="Absolute tolerance for numerical comparison in HDF5 files")
    
    return parser.parse_args()

def main():
    """
    @brief Main entry point of the application
    @details Handles the main workflow of file comparison including:
             - Setting up logging
             - Parsing arguments
             - Creating appropriate comparator
             - Performing comparison
             - Outputting results
    """
    logger = configure_logging()

    try:
        args = parse_arguments()
        
        # Set debug level if requested
        if args.debug:
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")

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

        # Prepare comparator kwargs based on file type and arguments
        comparator_kwargs = {
            "encoding": args.encoding,
            "chunk_size": args.chunk_size,
            "verbose": args.verbose or args.debug,  # Enable verbose mode if debug is enabled
            "num_threads": args.num_threads
        }
        
        # Add file type specific arguments
        if file_type == "json" and args.json_compare_mode:
            comparator_kwargs["compare_mode"] = args.json_compare_mode
            if args.json_key_field:
                key_fields = [field.strip() for field in args.json_key_field.split(',')]
                comparator_kwargs["key_field"] = key_fields[0] if len(key_fields) == 1 else key_fields
                logger.info(f"Using key field(s): {comparator_kwargs['key_field']} for JSON comparison")
        
        if file_type == "h5":
            if args.h5_table:
                tables = [table.strip() for table in args.h5_table.split(',')]
                comparator_kwargs["tables"] = tables
                logger.info(f"Comparing HDF5 tables: {tables}")
            if args.h5_table_regex:
                comparator_kwargs["table_regex"] = args.h5_table_regex
                logger.info(f"Using table regex pattern: {args.h5_table_regex}")
            comparator_kwargs["structure_only"] = args.h5_structure_only
            comparator_kwargs["show_content_diff"] = args.h5_show_content_diff
            comparator_kwargs["rtol"] = args.h5_rtol
            comparator_kwargs["atol"] = args.h5_atol
            if args.h5_structure_only:
                logger.info("Only comparing HDF5 file structure")
            logger.info(f"Using numerical comparison tolerances: rtol={args.h5_rtol}, atol={args.h5_atol}")
            comparator_kwargs["debug"] = args.debug
        
        if file_type == "binary":
            comparator_kwargs["similarity"] = args.similarity

        # Create comparator instance
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
    """
    @brief Detect the type of file based on its extension
    @param file_path Path to the file to analyze
    @return str: Detected file type ('text', 'json', 'xml', 'csv', 'h5', or 'binary')
    """
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
    elif extension in ['.h5', '.hdf5', '.he5']:
        return 'h5'
    else:
        # Default to binary comparison for unknown extensions
        return 'binary'

def format_result(result, output_format):
    """
    @brief Format the comparison result according to the specified output format
    @param result ComparisonResult object containing the comparison results
    @param output_format Desired output format ('text', 'json', or 'html')
    @return str: Formatted comparison result
    """
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