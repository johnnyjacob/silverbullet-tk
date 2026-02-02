#!/usr/bin/env python3
"""
Logseq to SilverBullet v2 Migration Script

This script migrates Logseq markdown files to SilverBullet v2 format:
- Processes journals/ and pages/ directories from Logseq
- Converts journal date format from YYYY_MM_DD to YYYY-MM-DD
- Converts page filenames with ___ to nested directories (e.g., foo___bar.md → foo/bar.md)
- Migrates assets folder with images and other media
- Updates date references, page links, and asset links in content
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import calendar

class LogseqToSilverBulletMigrator:
    def __init__(self, source_dir, target_dir):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        
        # Logseq source directories
        self.logseq_journals_dir = self.source_dir / "journals"
        self.logseq_pages_dir = self.source_dir / "pages"
        self.logseq_assets_dir = self.source_dir / "assets"
        
        # SilverBullet target directories
        # Note: journals go in root, not in a subdirectory
        self.assets_dir = self.target_dir / "assets"
        
        # Logseq uses YYYY_MM_DD format for journal files
        self.logseq_date_pattern = re.compile(r'^(\d{4})_(\d{2})_(\d{2})\.md$')
        
        # Month name to number mapping
        self.month_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'sept': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12
        }
    
    def parse_natural_date(self, date_str):
        """Parse natural language dates like 'Nov 6th, 2025' or 'January 1st, 2024'
        
        Returns: YYYY-MM-DD string or None if parsing fails
        """
        # Remove ordinal suffixes (st, nd, rd, th)
        date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)
        
        # Try patterns like "Nov 6, 2025" or "November 6, 2025"
        # Pattern: Month Day, Year
        pattern1 = r'^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$'
        match = re.match(pattern1, date_str.strip())
        
        if match:
            month_str, day_str, year_str = match.groups()
            month_str_lower = month_str.lower()
            
            if month_str_lower in self.month_map:
                month = self.month_map[month_str_lower]
                day = int(day_str)
                year = int(year_str)
                
                # Validate date
                try:
                    datetime(year, month, day)
                    return f"{year:04d}-{month:02d}-{day:02d}"
                except ValueError:
                    return None
        
        # Try pattern like "6 Nov 2025" or "6 November 2025"
        # Pattern: Day Month Year
        pattern2 = r'^(\d{1,2})\s+([A-Za-z]+),?\s+(\d{4})$'
        match = re.match(pattern2, date_str.strip())
        
        if match:
            day_str, month_str, year_str = match.groups()
            month_str_lower = month_str.lower()
            
            if month_str_lower in self.month_map:
                month = self.month_map[month_str_lower]
                day = int(day_str)
                year = int(year_str)
                
                # Validate date
                try:
                    datetime(year, month, day)
                    return f"{year:04d}-{month:02d}-{day:02d}"
                except ValueError:
                    return None
        
        return None
        
    def setup_target_directory(self):
        """Create target directory structure"""
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created target directory: {self.target_dir}")
        print(f"✓ Created assets directory: {self.assets_dir}")
    
    def is_journal_file(self, filename):
        """Check if a file is a Logseq journal entry"""
        return bool(self.logseq_date_pattern.match(filename))
    
    def convert_journal_filename(self, logseq_filename):
        """Convert Logseq journal filename to SilverBullet format
        
        Logseq: YYYY_MM_DD.md
        SilverBullet: YYYY-MM-DD.md
        """
        match = self.logseq_date_pattern.match(logseq_filename)
        if match:
            year, month, day = match.groups()
            return f"{year}-{month}-{day}.md"
        return logseq_filename
    
    def convert_page_path(self, logseq_filename):
        """Convert Logseq page filename to SilverBullet path
        
        Logseq uses ___ (triple underscore) to represent nested pages:
        - foo___bar.md → foo/bar.md
        - foo___bar___baz.md → foo/bar/baz.md
        
        Returns a Path object relative to target_dir
        """
        # Remove .md extension
        name_without_ext = logseq_filename[:-3] if logseq_filename.endswith('.md') else logseq_filename
        
        # Replace ___ with /
        if '___' in name_without_ext:
            path_parts = name_without_ext.split('___')
            # Last part is the filename, rest are directories
            if len(path_parts) > 1:
                return Path(*path_parts[:-1]) / f"{path_parts[-1]}.md"
        
        # No ___ found, return as-is
        return Path(logseq_filename)
    
    def convert_content(self, content, is_journal=False):
        """Convert content from Logseq to SilverBullet format
        
        This handles:
        - Date references in content: [[YYYY_MM_DD]] → [[YYYY-MM-DD]]
        - Natural language dates: [[Nov 6th, 2025]] → [[2025-11-06]]
        - Page links with ___: [[foo___bar]] → [[foo/bar]]
        - Asset links: ../assets/image.png → assets/image.png (or keep as-is)
        - Tasks: Logseq task syntax → SilverBullet task syntax
        """
        # Convert Logseq tasks to SilverBullet format
        # Logseq uses: TODO, DOING, DONE, LATER, NOW, WAITING, CANCELED
        # SilverBullet uses standard markdown: - [ ], - [x]
        
        # Map Logseq task states
        # TODO/LATER/NOW/WAITING → [ ] (unchecked)
        content = re.sub(r'^(\s*)[-*]\s+(TODO|LATER|NOW|WAITING)\s+', r'\1- [ ] ', content, flags=re.MULTILINE)
        
        # DOING → [ ] (unchecked, but we could mark it specially)
        content = re.sub(r'^(\s*)[-*]\s+DOING\s+', r'\1- [ ] **DOING:** ', content, flags=re.MULTILINE)
        
        # DONE → [x] (checked)
        content = re.sub(r'^(\s*)[-*]\s+DONE\s+', r'\1- [x] ', content, flags=re.MULTILINE)
        
        # CANCELED → [x] (checked, with strikethrough)
        content = re.sub(r'^(\s*)[-*]\s+CANCELED\s+', r'\1- [x] ~~', content, flags=re.MULTILINE)
        # Add closing strikethrough at end of line for CANCELED tasks
        content = re.sub(r'^((\s*)- \[x\] ~~.*)$', r'\1~~', content, flags=re.MULTILINE)
        
        # Convert date references from [[YYYY_MM_DD]] to [[YYYY-MM-DD]]
        content = re.sub(
            r'\[\[(\d{4})_(\d{2})_(\d{2})\]\]',
            r'[[\1-\2-\3]]',
            content
        )
        
        # Convert natural language date references
        # This handles [[Nov 6th, 2025]], [[January 1st, 2024]], etc.
        def replace_natural_date(match):
            date_str = match.group(1)
            parsed_date = self.parse_natural_date(date_str)
            if parsed_date:
                return f"[[{parsed_date}]]"
            return match.group(0)  # Keep original if parsing fails
        
        # Match dates like "Nov 6th, 2025" or "January 1, 2024"
        # Look for month names followed by day and year
        content = re.sub(
            r'\[\[([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})\]\]',
            replace_natural_date,
            content
        )
        
        # Also handle "6 Nov 2025" format
        content = re.sub(
            r'\[\[(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+,?\s+\d{4})\]\]',
            replace_natural_date,
            content
        )
        
        # Convert page links with ___ to /
        # This handles [[foo___bar]] → [[foo/bar]]
        def replace_page_link(match):
            page_name = match.group(1)
            if '___' in page_name:
                return f"[[{page_name.replace('___', '/')}]]"
            return match.group(0)
        
        content = re.sub(
            r'\[\[([^\]]+)\]\]',
            replace_page_link,
            content
        )
        
        # Convert asset references
        # Logseq uses ../assets/ or assets/ paths
        # Normalize to assets/ for SilverBullet
        content = re.sub(
            r'\.\./assets/',
            'assets/',
            content
        )
        
        return content
    
    def migrate_journal_file(self, source_file):
        """Migrate a journal file from Logseq to SilverBullet"""
        filename = source_file.name
        
        # Read the original content
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"✗ Error reading journal {filename}: {e}")
            return False
        
        # Convert filename and content
        new_filename = self.convert_journal_filename(filename)
        # Journals go in the root directory, not in a subdirectory
        target_file = self.target_dir / new_filename
        converted_content = self.convert_content(content, is_journal=True)
        
        # Write the converted content
        try:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            print(f"✓ Migrated journal: {filename} → {new_filename}")
            return True
        except Exception as e:
            print(f"✗ Error writing {target_file}: {e}")
            return False
    
    def migrate_page_file(self, source_file):
        """Migrate a page file from Logseq to SilverBullet"""
        filename = source_file.name
        
        # Read the original content
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"✗ Error reading page {filename}: {e}")
            return False
        
        # Convert filename/path (handle __ → /)
        relative_path = self.convert_page_path(filename)
        target_file = self.target_dir / relative_path
        
        # Create parent directories if needed
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert content
        converted_content = self.convert_content(content, is_journal=False)
        
        # Write the converted content
        try:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(converted_content)
            print(f"✓ Migrated page: {filename} → {relative_path}")
            return True
        except Exception as e:
            print(f"✗ Error writing {target_file}: {e}")
            return False
    
    def migrate_assets(self):
        """Migrate assets folder (images and other media) from Logseq to SilverBullet"""
        if not self.logseq_assets_dir.exists():
            print(f"⚠ Warning: Assets directory not found: {self.logseq_assets_dir}")
            return 0
        
        print(f"\n{'='*60}")
        print("Processing Assets")
        print(f"{'='*60}\n")
        
        assets_count = 0
        errors = 0
        
        # Walk through all files in assets directory
        for root, dirs, files in os.walk(self.logseq_assets_dir):
            root_path = Path(root)
            
            # Calculate relative path from logseq assets dir
            rel_path = root_path.relative_to(self.logseq_assets_dir)
            
            # Create corresponding directory in target
            target_subdir = self.assets_dir / rel_path
            target_subdir.mkdir(parents=True, exist_ok=True)
            
            # Copy all files
            for file in files:
                source_file = root_path / file
                target_file = target_subdir / file
                
                try:
                    shutil.copy2(source_file, target_file)
                    rel_display = Path(rel_path) / file if str(rel_path) != '.' else file
                    print(f"✓ Copied asset: {rel_display}")
                    assets_count += 1
                except Exception as e:
                    print(f"✗ Error copying {source_file}: {e}")
                    errors += 1
        
        print(f"\nTotal assets migrated: {assets_count}")
        if errors > 0:
            print(f"Errors: {errors}")
        
        return assets_count
    
    def migrate_all(self):
        """Migrate all markdown files from Logseq to SilverBullet"""
        if not self.source_dir.exists():
            print(f"✗ Error: Source directory does not exist: {self.source_dir}")
            return
        
        print(f"\n🚀 Starting migration from {self.source_dir} to {self.target_dir}\n")
        
        self.setup_target_directory()
        
        # Track statistics
        stats = {
            'journals': 0,
            'pages': 0,
            'assets': 0,
            'errors': 0
        }
        
        # Process journals directory
        print(f"\n{'='*60}")
        print("Processing Journals")
        print(f"{'='*60}\n")
        
        if self.logseq_journals_dir.exists():
            journal_files = list(self.logseq_journals_dir.glob('*.md'))
            print(f"Found {len(journal_files)} journal files\n")
            
            for journal_file in journal_files:
                if self.migrate_journal_file(journal_file):
                    stats['journals'] += 1
                else:
                    stats['errors'] += 1
        else:
            print(f"⚠ Warning: Journals directory not found: {self.logseq_journals_dir}")
        
        # Process pages directory
        print(f"\n{'='*60}")
        print("Processing Pages")
        print(f"{'='*60}\n")
        
        if self.logseq_pages_dir.exists():
            page_files = list(self.logseq_pages_dir.glob('*.md'))
            print(f"Found {len(page_files)} page files\n")
            
            for page_file in page_files:
                if self.migrate_page_file(page_file):
                    stats['pages'] += 1
                else:
                    stats['errors'] += 1
        else:
            print(f"⚠ Warning: Pages directory not found: {self.logseq_pages_dir}")
        
        # Process assets directory
        stats['assets'] = self.migrate_assets()
        
        # Print summary
        print(f"\n{'='*60}")
        print("Migration Summary")
        print(f"{'='*60}")
        print(f"Journal entries migrated: {stats['journals']}")
        print(f"Pages migrated: {stats['pages']}")
        print(f"Assets migrated: {stats['assets']}")
        print(f"Errors: {stats['errors']}")
        print(f"Total files processed: {stats['journals'] + stats['pages'] + stats['assets']}")
        print(f"\n✓ Migration complete! Files are in: {self.target_dir}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate Logseq markdown files to SilverBullet v2 format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/logseq /path/to/silverbullet
  %(prog)s ./my-logseq-vault ./silverbullet-notes
  
The source directory should contain journals/ and pages/ subdirectories.
        """
    )
    
    parser.add_argument(
        'source_dir',
        help='Path to Logseq root directory (containing journals/ and pages/ folders)'
    )
    
    parser.add_argument(
        'target_dir',
        help='Path to SilverBullet target directory (will be created if needed)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be migrated without actually copying files'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")
        # TODO: Implement dry run mode
        print("Dry run mode not yet implemented")
        return
    
    migrator = LogseqToSilverBulletMigrator(args.source_dir, args.target_dir)
    migrator.migrate_all()


if __name__ == '__main__':
    main()