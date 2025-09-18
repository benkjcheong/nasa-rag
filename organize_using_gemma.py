#!/usr/bin/env python3
"""
Use Gemma to accurately extract authors from NASA papers
"""

import os
import re
from pathlib import Path
import requests
import json
import time

def extract_title_and_authors_with_gemma(content, pmc_id):
    """Use Gemma to extract title and authors from paper content"""
    
    # Find Abstract and Summary sections
    abstract_pos = content.lower().find('abstract')
    summary_pos = content.lower().find('summary')
    
    # Skip only if neither abstract nor summary is found
    if abstract_pos == -1 and summary_pos == -1:
        return None, None  # No abstract or summary found, skip this file
    
    # Use whichever comes first (or the one that exists)
    if abstract_pos != -1 and summary_pos != -1:
        text_sample = content[:min(abstract_pos, summary_pos)]
    elif abstract_pos != -1:
        text_sample = content[:abstract_pos]
    else:
        text_sample = content[:summary_pos]
    
    prompt = f"""Extract the title and all author names from this scientific paper text. 

Return in this exact format:
Title: [paper title]
Authors: [author1, author2, author3, ...]

Text:
{text_sample}

Extraction:"""

    try:
        # Using Ollama API (adjust URL if needed)
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   'model': 'gemma2:2b',
                                   'prompt': prompt,
                                   'stream': False,
                                   'options': {
                                       'temperature': 0.1,
                                       'top_p': 0.9
                                   }
                               },
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get('response', '').strip()
            
            # Parse title and authors
            title = "Unknown Title"
            authors = []
            
            for line in response_text.split('\n'):
                line = line.strip()
                if line.startswith('Title:'):
                    title = line.replace('Title:', '').strip()
                elif line.startswith('Authors:'):
                    authors_text = line.replace('Authors:', '').strip()
                    authors = [name.strip() for name in authors_text.split(',') if name.strip()]
                    authors = authors[:10]  # Limit to reasonable number
            
            return title, authors
            
    except Exception as e:
        print(f"Error with Gemma for {pmc_id}: {e}")
    
    return "Unknown Title", []

def process_files_with_gemma(input_dir, output_dir):
    """Process files using Gemma for author extraction"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    txt_files = list(input_path.glob('PMC*.txt'))
    print(f"Processing {len(txt_files)} files with Gemma...")
    
    processed = 0
    skipped_files = []
    for file_path in txt_files:
        pmc_id = file_path.stem
        output_file = output_path / f'{pmc_id}_gemma_cleaned.txt'
        
        # Skip if already processed
        if output_file.exists():
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get title and authors from Gemma
            title, authors = extract_title_and_authors_with_gemma(content, pmc_id)
            
            if title is None:
                skipped_files.append(pmc_id)
                continue
            
            # Find Abstract and Summary positions
            abstract_pos = content.lower().find('abstract')
            summary_pos = content.lower().find('summary')
            
            # Determine starting position (use whichever comes first)
            if abstract_pos != -1 and summary_pos != -1:
                start_pos = min(abstract_pos, summary_pos)
            elif abstract_pos != -1:
                start_pos = abstract_pos
            else:
                start_pos = summary_pos
            
            # Create clean content: Title + Authors + content from Abstract/Summary onwards
            clean_content = f"Title: {title}\n\nAuthors: "
            if authors:
                clean_content += ", ".join(authors)
            else:
                clean_content += "Could not extract"
            
            clean_content += "\n\n" + content[start_pos:]
            
            # Write cleaned file
            output_file = output_path / f'{pmc_id}_gemma_cleaned.txt'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            
            processed += 1
            if processed % 10 == 0:
                print(f"Processed {processed}/{len(txt_files)} files...")
                time.sleep(1)  # Brief pause to avoid overwhelming the API
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"Completed processing {processed} files with Gemma")
    if skipped_files:
        print(f"\nSkipped {len(skipped_files)} files without 'Abstract' or 'Summary':")
        for file_id in skipped_files:
            print(f"  - {file_id}")

def main():
    current_dir = Path(__file__).parent
    input_dir = current_dir
    output_dir = current_dir / 'gemma_organized'
    
    print("Starting Gemma-based author extraction...")
    process_files_with_gemma(input_dir, output_dir)
    print("Gemma processing complete!")

if __name__ == "__main__":
    main()