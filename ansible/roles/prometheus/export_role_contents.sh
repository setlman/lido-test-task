#!/bin/bash

# Script to export all files from the current directory into a single text file with separators.

# Define the output file
OUTPUT_FILE="role_contents.txt"

# Get the name of the script to exclude it from processing
SCRIPT_NAME=$(basename "$0")

# Initialize/Empty the output file
> "$OUTPUT_FILE"

# Find all files in the current directory and its subdirectories,
# excluding the output file and the script itself
find . -type f ! -name "$OUTPUT_FILE" ! -name "$SCRIPT_NAME" | sort | while read -r file; do
  # Remove the leading './' from the file path for cleaner display
  clean_path="${file#./}"
  
  # Write the file path as a header
  echo "File: $clean_path" >> "$OUTPUT_FILE"
  echo "------------------------" >> "$OUTPUT_FILE"
  
  # Append the file content
  cat "$file" >> "$OUTPUT_FILE"
  
  # Add gaps for readability
  echo -e "\n\n" >> "$OUTPUT_FILE"
done

echo "All files have been exported to '$OUTPUT_FILE'."
