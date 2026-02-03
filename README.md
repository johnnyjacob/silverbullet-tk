# Logseq to SilverBullet v2 Migration Script

This script migrates your Logseq markdown files to SilverBullet v2 format.

## What it does

- **Processes Logseq's directory structure**: Reads from `journals/`, `pages/`, and `assets/` directories
- **Converts journal dates** from Logseq's `YYYY_MM_DD.md` to SilverBullet's `YYYY-MM-DD.md` (in root directory)
- **Converts natural language dates** like `[[Nov 6th, 2025]]` to journal links `[[2025-11-06]]`
- **Converts Logseq tasks** to standard markdown checkboxes
- **Creates nested directories** from page names with `___` (e.g., `foo___bar.md` → `foo/bar.md`)
- **Migrates all assets** including images and other media files
- **Updates date references** in content from `[[YYYY_MM_DD]]` to `[[YYYY-MM-DD]]`
- **Updates page links** in content from `[[foo___bar]]` to `[[foo/bar]]`
- **Updates asset paths** from `../assets/` to `assets/`
- **Preserves all content** and maintains markdown formatting

## Requirements

- Python 3.6 or higher (no external dependencies needed)

## Usage

### Basic Usage

```bash
python3 migrate.py <logseq_root_directory> <target_directory>
```

### Example

```bash
# Migrate from Logseq vault to a new SilverBullet directory
python3 migrate.py ~/logseq ~/silverbullet-notes

# Or with relative paths
python3 migrate.py ./my-logseq-vault ./silverbullet
```

### Arguments

- `source_dir` - Path to your Logseq root directory (the one containing `journals/` and `pages/` folders)
- `target_dir` - Path where you want the SilverBullet files (will be created if it doesn't exist)

## What gets migrated

### Journal Files (from `journals/` directory)
Files matching the pattern `YYYY_MM_DD.md` in the journals directory are placed in the root:
- `2024_01_15.md` → `2024-01-15.md`
- `2023_12_25.md` → `2023-12-25.md`

### Regular Pages (from `pages/` directory)
All `.md` files in the pages directory:

**Simple pages:**
- `Project Ideas.md` → `Project Ideas.md`
- `Meeting Notes.md` → `Meeting Notes.md`

**Nested pages (with ___):**
- `Work___Projects.md` → `Work/Projects.md`
- `Work___Projects___Q1.md` → `Work/Projects/Q1.md`
- `Personal___Health___Exercise.md` → `Personal/Health/Exercise.md`

### Assets (from `assets/` directory)
All files in the assets directory (images, PDFs, etc.) are copied to SilverBullet:
- `assets/screenshot.png` → `assets/screenshot.png`
- `assets/documents/report.pdf` → `assets/documents/report.pdf`
- Subdirectory structure is preserved

### Task Conversion
Logseq tasks are converted to standard markdown checkboxes:
- `- TODO Buy groceries` → `- [ ] Buy groceries`
- `- DOING Write report` → `- [ ] **DOING:** Write report`
- `- DONE Finish homework` → `- [x] Finish homework`
- `- LATER Plan vacation` → `- [ ] Plan vacation`
- `- NOW Call client` → `- [ ] Call client`
- `- WAITING Response from team` → `- [ ] Response from team`
- `- CANCELED Old task` → `- [x] ~~Old task~~`

### Wiki Link Restructuring
Lines starting with wiki links followed by text are restructured to avoid being interpreted as tasks:

**Before (Logseq):**
```
- [[Work/Issues/ISSUE-123]] and some text
- [[Project___Name]] description here
```

**After (SilverBullet):**
```
- [Work/Issues/ISSUE-123]
  - and some text
- [Project/Name]
  - description here
```

The link becomes a list item with single brackets `[link]`, and any text after it becomes an indented sub-item. This format works perfectly in SilverBullet as a clickable link to the page.

**Note about other bracket patterns:** 
If you have patterns like `- [some text] content` in your Logseq notes (not wiki links or tasks), the brackets will be removed:
- `- [note] This is important` → `- note This is important`
- `- [tag] Category item` → `- tag Category item`

Real checkboxes `- [ ]` and `- [x]` are always preserved.

### Content Conversion
Links in your content are also updated:
- **Date references:** `[[2024_01_15]]` → `[[2024-01-15]]`
- **Natural language dates:** `[[Nov 6th, 2025]]` → `[[2025-11-06]]`
- **Natural language dates:** `[[January 1st, 2024]]` → `[[2024-01-01]]`
- **Alternative date format:** `[[6 Nov 2025]]` → `[[2025-11-06]]`
- **Page links:** `[[Work___Projects]]` → `[[Work/Projects]]`
- **Nested page links:** `[[Foo___Bar___Baz]]` → `[[Foo/Bar/Baz]]`
- **Asset paths:** `../assets/image.png` → `assets/image.png`

## Directory Structure

**Before (Logseq):**
```
my-logseq-vault/
├── journals/
│   ├── 2024_01_15.md
│   └── 2024_01_16.md
├── pages/
│   ├── Project Ideas.md
│   ├── Meeting Notes.md
│   ├── Work___Projects.md
│   └── Work___Projects___Q1.md
└── assets/
    ├── screenshot.png
    ├── diagram.jpg
    └── documents/
        └── report.pdf
```

**After (SilverBullet):**
```
silverbullet/
├── 2024-01-15.md          (journal in root)
├── 2024-01-16.md          (journal in root)
├── assets/
│   ├── screenshot.png
│   ├── diagram.jpg
│   └── documents/
│       └── report.pdf
├── Project Ideas.md
├── Meeting Notes.md
└── Work/
    └── Projects/
        ├── Q1.md
        └── Projects.md (from Work___Projects.md)
```

**Note:** Journal files are placed in the root directory alongside your pages, not in a separate `journals/` subdirectory. The nested structure for pages creates a more organized hierarchy.

## Tips

1. **Backup first**: Always backup your Logseq data before running the migration
2. **Fresh target**: Use a new/empty directory as your target to avoid conflicts
3. **Check your source**: Make sure you're pointing to the Logseq root directory (the one containing `journals/`, `pages/`, and `assets/`)
4. **Review output**: The script shows what it's doing - review the output for any errors
5. **Nested pages**: If you have pages with `___` (triple underscore) in the name, they'll be converted to nested directories automatically
6. **Assets**: All files in the assets folder will be copied while preserving the directory structure
7. **Natural language dates**: Dates like "Nov 6th, 2025" or "January 1st, 2024" in links will be converted to ISO format (YYYY-MM-DD) and linked to the appropriate journal
8. **Tasks**: Logseq TODO/DOING/DONE tasks are automatically converted to standard markdown checkboxes that work in SilverBullet

## Troubleshooting

**"Source directory does not exist"**
- Check that the path to your Logseq root directory is correct
- Use absolute paths if relative paths aren't working

**"Journals directory not found" or "Pages directory not found"**
- Make sure you're pointing to the Logseq root directory, not the `journals/` or `pages/` subdirectory
- Verify your Logseq vault has these standard directories

**"Assets directory not found"**
- This is just a warning - it's okay if you don't have an assets folder
- The migration will continue normally for journals and pages

**Nested pages not working correctly**
- Check that your page filenames use `___` (triple underscore) to separate hierarchy levels
- The script will create the necessary subdirectories automatically

**Images not showing up**
- Verify that asset links in your markdown reference `assets/` or `../assets/`
- The script normalizes these to `assets/` for SilverBullet

## After Migration

1. Point SilverBullet to your new target directory
2. Verify your journal entries are in the `journals/` folder
3. Check that page links work correctly
4. Review any error messages from the migration

## License

Free to use and modify as needed.