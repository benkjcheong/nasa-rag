#!/usr/bin/env python3
import os
import re

def remove_references_section(file_path):
    """Remove the References section from a text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the References section (case insensitive)
        # Look for "References" at the beginning of a line, possibly preceded by whitespace
        pattern = r'\n\s*References\s*\n.*$'
        
        # Remove everything from "References" to the end of the file
        cleaned_content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        # Write back the cleaned content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    # Get current directory (should be the txt directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all txt files in the directory
    txt_files = [f for f in os.listdir(current_dir) if f.endswith('.txt')]
    
    if not txt_files:
        print("No txt files found in the current directory.")
        return
    
    print(f"Found {len(txt_files)} txt files.")
    
    # Process each file
    processed = 0
    for txt_file in txt_files:
        file_path = os.path.join(current_dir, txt_file)
        print(f"Processing {txt_file}...")
        
        if remove_references_section(file_path):
            processed += 1
            print(f"  ✓ References section removed from {txt_file}")
        else:
            print(f"  ✗ Failed to process {txt_file}")
    
    print(f"\nCompleted: {processed}/{len(txt_files)} files processed successfully.")

if __name__ == "__main__":
    main()