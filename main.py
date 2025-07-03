#!/usr/bin/env python3

import os
import re
import argparse
import logging
from pathlib import Path

# Configure logging for clean output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Headers to be removed along with the subsequent blank line
HEADERS_TO_REMOVE = [
    "##### **Output**",
    "##### **Code**",
]

def reformat_markdown_file(file_path: Path) -> None:
    """
    Parses and reformats a single Markdown file with state-aware logic.

    Args:
        file_path: The path to the markdown file to process.
    """
    logging.info(f"Processing file: {file_path}")

    try:
        with file_path.open('r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        logging.error(f"Could not read file {file_path}. Error: {e}")
        return

    original_content = "".join(lines)
    new_lines = []
    changes_made = False
    in_code_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped_line = line.strip()

        # Rule 1: Header Removal (only applies outside code blocks)
        if not in_code_block and stripped_line in HEADERS_TO_REMOVE:
            changes_made = True
            logging.info(f"  - Removing header '{stripped_line}' at line {i + 1}")
            i += 1
            # Also skip the next line if it's blank
            if i < len(lines) and lines[i].strip() == "":
                i += 1
            continue

        # Rule 2: Code block annotation (state-aware)
        # Use regex to match a code fence and capture the language
        match = re.match(r'^```(\S*)$', stripped_line)

        if match:
            if not in_code_block:
                # This is an OPENING code fence
                in_code_block = True
                lang = match.group(1)
                
                # Only add 'output' if no language is specified
                if not lang:
                    new_lines.append("```output\n")
                    changes_made = True
                    logging.info(f"  - Annotating un-tagged code block at line {i + 1} with 'output'")
                else:
                    # Language already exists, leave it as is
                    new_lines.append(line)
            else:
                # This is a CLOSING code fence
                in_code_block = False
                new_lines.append(line)
        else:
            # Not a code fence, just append the line
            new_lines.append(line)
        
        i += 1
    
    new_content = "".join(new_lines)

    # Only write back to the file if content has actually changed
    if changes_made and new_content != original_content:
        try:
            with file_path.open('w', encoding='utf-8') as f:
                f.write(new_content)
            logging.info(f"Successfully reformatted and saved {file_path}")
        except Exception as e:
            logging.error(f"Could not write to file {file_path}. Error: {e}")
    else:
        logging.info(f"  - No changes needed for {file_path}")

def main():
    """Main function to parse arguments and walk through the directory."""
    parser = argparse.ArgumentParser(
        description="A script to reformat specific items in Markdown files."
    )
    parser.add_argument(
        "--directory",
        type=str,
        required=True,
        help="The directory containing Markdown files to process.",
    )
    args = parser.parse_args()

    target_dir = Path(args.directory)
    if not target_dir.is_dir():
        logging.error(f"Error: The provided path '{target_dir}' is not a valid directory.")
        return

    logging.info(f"Starting scan in directory: {target_dir.resolve()}")

    md_files = list(target_dir.rglob("*.md"))
    
    if not md_files:
        logging.warning("No Markdown (.md) files found in the specified directory.")
        return

    for md_file in md_files:
        reformat_markdown_file(md_file)
    
    logging.info("Processing complete.")

if __name__ == "__main__":
    main()
