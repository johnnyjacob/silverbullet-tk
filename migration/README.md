# Migration Tools

Scripts to help you migrate to SilverBullet and organize your notes.

## Tools

### 1. migrate.py - Logseq to SilverBullet Migration

Complete migration script that converts your Logseq vault to SilverBullet format.

#### What it does

- **Processes Logseq's directory structure**: Reads from `journals/`, `pages/`, and `assets/` directories
- **Converts journal dates** from Logseq's `YYYY_MM_DD.md` to SilverBullet's `YYYY-MM-DD.md` (in root directory)
- **Converts natural language dates** like `[[Nov 6th, 2025]]` to `Nov 6th, 2025 [[2025-11-06]]` with readable text and ISO link
- **Formats date links** to show natural language followed by journal link
- **Converts Logseq tasks** to standard markdown checkboxes
- **Converts LOGBOOK entries** to SilverBullet attributes for time tracking
- **Creates nested directories** from page names with `___` (e.g., `foo___bar.md` → `foo/bar.md`)
- **Converts colons to dashes** in filenames (e.g., `Project: Name.md` → `Project- Name.md`)
- **Migrates all assets** including images and other media files
- **Updates all internal links** automatically

#### Requirements

- Python 3.6 or higher (no external dependencies needed)

#### Usage

```bash
python3 migrate.py <logseq_root_directory> <target_directory>
```

**Example:**
```bash
python3 migrate.py ~/logseq ~/silverbullet-notes
```

#### Important Notes

1. **Backup first**: Always backup your Logseq data before running the migration
2. **Fresh target**: Use a new/empty directory as your target to avoid conflicts
3. **Check your source**: Make sure you're pointing to the Logseq root directory (the one containing `journals/`, `pages/`, and `assets/`)
4. **Review output**: The script shows what it's doing - review the output for any errors

For detailed migration information, see [MIGRATION_README.md](MIGRATION_README.md).

---

### 2. update_journal_backlinks.py - Journal Organization Tool

Reorganizes journal pages from flat structure to nested folder structure and updates all backlinks automatically.

#### What it does

Converts journal pages from:
```
2024-01-15.md
2024-01-16.md
2024-02-20.md
```

To nested structure:
```
Journals/
  2024/
    01/
      15.md
      16.md
    02/
      20.md
```

And automatically updates all backlinks throughout your space:
- `[[2024-01-15]]` → `[[Journals/2024/01/15]]`
- `[[2024-01-15|Monday]]` → `[[Journals/2024/01/15|Monday]]`

#### Requirements

- Python 3.6 or higher (no external dependencies needed)

#### Configuration

Edit the script to set:

```python
SPACE_PATH = "/path/to/your/silverbullet/space"  # Your SilverBullet space path
DRY_RUN = True  # Set to False to actually perform the rename
```

#### Usage

**Step 1: Dry Run (recommended)**
```bash
python3 update_journal_backlinks.py
```

This will show you what would be changed without making any modifications.

**Step 2: Apply Changes**

After reviewing the dry run output, set `DRY_RUN = False` in the script and run again:
```bash
python3 update_journal_backlinks.py
```

#### Output Example

```
Scanning space: /home/user/silverbullet
Mode: DRY RUN
============================================================

Found 150 date pages to rename

📄 2024-01-15 → Journals/2024/01/15
   Found 5 backlinks
   ✓ Updated: Projects/Work Notes.md
   ✓ Updated: 2024-01-16.md
   ✓ Renamed page

============================================================
Summary:
  Pages renamed: 150
  Backlinks updated: 342

⚠️  This was a DRY RUN - no changes were made
Set DRY_RUN = False to apply changes
```

#### Important Notes

1. **Backup first**: Always backup your SilverBullet space before running
2. **Test with dry run**: Review the output with `DRY_RUN = True` first
3. **Close SilverBullet**: Close your SilverBullet instance before running to avoid conflicts
4. **Review changes**: After running, verify a few pages to ensure links work correctly

---

## Troubleshooting

### Migration Issues

**"Source directory does not exist"**
- Check that the path to your Logseq root directory is correct
- Use absolute paths if relative paths aren't working

**"Journals directory not found" or "Pages directory not found"**
- Make sure you're pointing to the Logseq root directory, not a subdirectory
- Verify your Logseq vault has these standard directories

**Nested pages not working correctly**
- Check that your page filenames use `___` (triple underscore) to separate hierarchy levels

### Journal Backlink Updater Issues

**No pages found**
- Verify `SPACE_PATH` points to your SilverBullet space directory
- Check that you have journal pages in `YYYY-MM-DD.md` format

**Some backlinks not updated**
- The script only updates standard wiki link formats `[[page]]` and `[[page|alias]]`
- Custom link formats may need manual updating

**Script runs but no changes made**
- Make sure `DRY_RUN = False` in the script configuration
- Check file permissions on your space directory

---

## Tips

- **Migration**: Run the Logseq migration once when initially switching to SilverBullet
- **Journal Organization**: Run the backlink updater anytime you want to reorganize your journal structure
- **Both scripts preserve your content**: They only modify filenames and links, not the content itself
- **Version control**: If your notes are in git, commit before running these scripts for easy rollback

---

## Support

For issues or questions:
- Check the [main repository README](../README.md)
- Review the detailed [migration documentation](MIGRATION_README.md)
- Open an issue on GitHub