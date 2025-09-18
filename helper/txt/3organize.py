#!/usr/bin/env python3
"""
3organize.py - Clean up NASA research papers by organizing authors at the top
Extracts authors and places them in a clean format at the beginning of each file
"""

import os
import re
from pathlib import Path

def extract_authors(content):
    """Extract author information from the paper content"""
    authors = []
    lines = content.split('\n')
    
    # Find the title line (usually the first substantial line after journal info)
    title_line = None
    for i, line in enumerate(lines[:20]):
        if len(line.strip()) > 50 and not line.startswith('Search in') and 'doi:' not in line:
            title_line = i
            break
    
    if title_line is None:
        return []
    
    # Look for authors after the title
    author_section_start = title_line + 1
    author_section_end = None
    
    # Find where author section ends (usually at "Author information" or similar)
    for i in range(author_section_start, min(len(lines), author_section_start + 100)):
        line = lines[i].strip()
        if any(marker in line.lower() for marker in ['author information', 'article notes', 'copyright', 'received', 'pmcid']):
            author_section_end = i
            break
    
    if author_section_end is None:
        author_section_end = min(len(lines), author_section_start + 50)
    
    # Extract author names from the author section
    current_author = None
    for i in range(author_section_start, author_section_end):
        line = lines[i].strip()
        
        # Skip empty lines and certain patterns
        if not line or line.startswith('Find articles') or line.startswith('Search in'):
            continue
            
        # Check if this looks like an author name (2-4 words, proper case)
        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+(?:\s[A-Z][a-z]+)*$', line) and len(line.split()) <= 4:
            # Avoid duplicates that appear twice
            if line not in authors:
                authors.append(line)
                current_author = line
        # Sometimes author names are repeated, skip the duplicate
        elif line == current_author:
            continue
    
    return authors

def get_title(content):
    """Extract the paper title"""
    lines = content.split('\n')
    
    # Look for the title (usually the first substantial line after journal info)
    for line in lines[:20]:
        line = line.strip()
        if (len(line) > 30 and 
            not line.startswith('Search in') and 
            'doi:' not in line.lower() and
            not line.startswith('Add to search') and
            not any(x in line.lower() for x in ['pmid', 'pmc', 'pubmed'])):
            return line
    
    return "Unknown Title"

def organize_file(file_path):
    """Clean up a single file by organizing authors at the top"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract PMC ID from filename
        pmc_id = Path(file_path).stem
        
        # Extract title and authors
        title = get_title(content)
        authors = extract_authors(content)
        
        # Create clean header
        clean_content = f"Paper ID: {pmc_id}\n"
        clean_content += f"Title: {title}\n\n"
        
        if authors:
            clean_content += "AUTHORS:\n"
            clean_content += "=" * 50 + "\n"
            for i, author in enumerate(authors, 1):
                clean_content += f"{i}. {author}\n"
            clean_content += "\n" + "=" * 50 + "\n\n"
        else:
            clean_content += "AUTHORS: Not clearly identified\n\n"
        
        # Add the rest of the content
        clean_content += "FULL CONTENT:\n"
        clean_content += "=" * 50 + "\n"
        clean_content += content
        
        return {
            'pmc_id': pmc_id,
            'title': title,
            'authors': authors,
            'clean_content': clean_content
        }
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def create_organized_files(input_dir, output_dir):
    """Create cleaned files with authors organized at the top"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Create subdirectories
    (output_path / 'cleaned_papers').mkdir(exist_ok=True)
    (output_path / 'author_index').mkdir(exist_ok=True)
    
    all_papers = {}
    author_papers = {}
    
    # Process all txt files
    txt_files = list(input_path.glob('PMC*.txt'))
    print(f"Processing {len(txt_files)} files...")
    
    for file_path in txt_files:
        organized_data = organize_file(file_path)
        if organized_data:
            pmc_id = organized_data['pmc_id']
            all_papers[pmc_id] = organized_data
            
            # Write cleaned individual file
            with open(output_path / 'cleaned_papers' / f'{pmc_id}_cleaned.txt', 'w', encoding='utf-8') as f:
                f.write(organized_data['clean_content'])
            
            # Group by authors
            for author in organized_data['authors']:
                if author not in author_papers:
                    author_papers[author] = []
                author_papers[author].append({
                    'pmc_id': pmc_id,
                    'title': organized_data['title']
                })
    
    # Write comprehensive author index
    with open(output_path / 'author_index' / 'complete_author_index.txt', 'w', encoding='utf-8') as f:
        f.write("COMPLETE AUTHOR INDEX\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total unique authors: {len(author_papers)}\n")
        f.write(f"Total papers processed: {len(all_papers)}\n\n")
        
        for author, papers in sorted(author_papers.items()):
            f.write(f"\n{author} ({len(papers)} papers)\n")
            f.write("-" * 50 + "\n")
            for paper in papers:
                f.write(f"  • {paper['pmc_id']}: {paper['title'][:80]}...\n")
    
    print(f"\nSUMMARY:")
    print(f"Processed {len(all_papers)} papers")
    print(f"Found {len(author_papers)} unique authors")
    print(f"Created cleaned files in: {output_path / 'cleaned_papers'}")
    print(f"Created author index in: {output_path / 'author_index'}")

def main():
    """Main function to run the organization script"""
    current_dir = Path(__file__).parent
    input_dir = current_dir
    output_dir = current_dir / 'organized'
    
    print("Starting paper organization...")
    create_organized_files(input_dir, output_dir)
    print("Organization complete!")

if __name__ == "__main__":
    main()