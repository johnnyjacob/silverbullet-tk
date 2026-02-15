#!/usr/bin/env python3
"""
Rename SilverBullet daily note pages from YYYY-MM-DD to Journals/YYYY/MM/DD format
and update all backlinks automatically.
"""

import re
import os
from pathlib import Path
from collections import defaultdict

# Configuration
SPACE_PATH = "/home/johnny/tmp/current-notes"  # Update this path
DRY_RUN = False  # Set to False to actually perform the rename

def find_date_pages(space_path):
    """Find all pages matching YYYY-MM-DD pattern."""
    date_pattern = re.compile(r'^(\d{4})-(\d{2})-(\d{2})\.md$')
    date_pages = []
    
    for file in Path(space_path).rglob('*.md'):
        match = date_pattern.match(file.name)
        if match:
            year, month, day = match.groups()
            old_path = file
            new_path = file.parent / "Journals" / year / month / f"{day}.md"
            date_pages.append({
                'old_path': old_path,
                'new_path': new_path,
                'old_name': file.stem,  # Without .md extension
                'new_name': f"Journals/{year}/{month}/{day}"
            })
    
    return date_pages

def find_backlinks(space_path, page_name):
    """Find all pages that link to the given page."""
    # Match [[page_name]] or [[page_name|alias]]
    link_pattern = re.compile(
        r'\[\[' + re.escape(page_name) + r'(?:\|[^\]]+)?\]\]'
    )
    
    backlinks = []
    
    for file in Path(space_path).rglob('*.md'):
        try:
            content = file.read_text(encoding='utf-8')
            if link_pattern.search(content):
                backlinks.append(file)
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    return backlinks

def update_backlinks_in_file(file_path, old_name, new_name, dry_run=True):
    """Update all references to old_name with new_name in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Replace [[old_name]] with [[new_name]]
        updated_content = re.sub(
            r'\[\[' + re.escape(old_name) + r'\]\]',
            f'[[{new_name}]]',
            content
        )
        
        # Replace [[old_name|alias]] with [[new_name|alias]]
        updated_content = re.sub(
            r'\[\[' + re.escape(old_name) + r'\|([^\]]+)\]\]',
            f'[[{new_name}|\\1]]',
            updated_content
        )
        
        if content != updated_content:
            if not dry_run:
                file_path.write_text(updated_content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error updating {file_path}: {e}")
        return False

def rename_page(old_path, new_path, dry_run=True):
    """Rename a page file."""
    if not dry_run:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.rename(new_path)
    return True

def main():
    space_path = Path(SPACE_PATH)
    
    if not space_path.exists():
        print(f"Error: Space path does not exist: {space_path}")
        return
    
    print(f"Scanning space: {space_path}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print("=" * 60)
    
    # Find all date pages to rename
    date_pages = find_date_pages(space_path)
    print(f"\nFound {len(date_pages)} date pages to rename\n")
    
    if not date_pages:
        print("No pages to rename!")
        return
    
    # Process each page
    total_backlinks_updated = 0
    
    for page in date_pages:
        print(f"\n📄 {page['old_name']} → {page['new_name']}")
        
        # Find backlinks
        backlinks = find_backlinks(space_path, page['old_name'])
        print(f"   Found {len(backlinks)} backlinks")
        
        # Update backlinks
        for backlink_file in backlinks:
            if update_backlinks_in_file(
                backlink_file, 
                page['old_name'], 
                page['new_name'], 
                dry_run=DRY_RUN
            ):
                print(f"   ✓ Updated: {backlink_file.relative_to(space_path)}")
                total_backlinks_updated += 1
        
        # Rename the page itself
        if rename_page(page['old_path'], page['new_path'], dry_run=DRY_RUN):
            print(f"   ✓ Renamed page")
    
    print("\n" + "=" * 60)
    print(f"Summary:")
    print(f"  Pages renamed: {len(date_pages)}")
    print(f"  Backlinks updated: {total_backlinks_updated}")
    
    if DRY_RUN:
        print("\n⚠️  This was a DRY RUN - no changes were made")
        print("Set DRY_RUN = False to apply changes")

if __name__ == "__main__":
    main()