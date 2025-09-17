#!/usr/bin/env python3
import os
import re

def remove_acknowledgements_section(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try different variations of acknowledgements
    for ack_word in ['Acknowledgements', 'Acknowledgments', 'ACKNOWLEDGEMENTS', 'ACKNOWLEDGMENTS']:
        if ack_word in content:
            content = content.split(ack_word)[0]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
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
    no_acknowledgements = []
    for txt_file in txt_files:
        file_path = os.path.join(current_dir, txt_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if any(ack in content.lower() for ack in ['acknowledgements', 'acknowledgments']):
            remove_acknowledgements_section(file_path)
            processed += 1
        else:
            no_acknowledgements.append(txt_file)
    
    print(f"Processed: {processed}/{len(txt_files)} files")
    print(f"Files with no Acknowledgements section: {no_acknowledgements}")

if __name__ == "__main__":
    main()