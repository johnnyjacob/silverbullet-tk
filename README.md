# SilverBullet Toolkit

A collection of tools, scripts, and resources for working with [SilverBullet](https://silverbullet.md/) - the extensible note-taking tool.

## 📁 Repository Structure

- **[migrate/](migrate/)** - Migration tools and scripts
  - Logseq to SilverBullet migration script
  - Journal backlink updater
- **configs/** *(coming soon)* - Configuration examples and templates
- **snippets/** *(coming soon)* - Code snippets and templates

## 🚀 Quick Start

More in QuickStart.md

### Migrating from Logseq

If you're migrating from Logseq to SilverBullet, check out the [migrate folder](migrate/) for the complete migration tool.

```bash
cd migrate
python3 migrate.py ~/logseq-vault ~/silverbullet-space
```

### Organizing Journal Pages

If you want to reorganize your journal pages from flat `YYYY-MM-DD.md` to nested `Journals/YYYY/MM/DD.md` structure:

```bash
cd migrate
python3 backlinks.py
```

## 🛠️ Tools

### Migration Scripts

- **migrate.py** - Complete Logseq to SilverBullet migration
  - Converts journal date formats
  - Handles nested pages (triple underscore to folders)
  - Migrates assets and images
  - Converts tasks and logbook entries
  - Updates all internal links

- **backlinks.py** - Journal organization tool
  - Renames journal pages to nested folder structure
  - Automatically updates all backlinks across your space
  - Dry-run mode for safe testing

## 📚 Resources

### SilverBullet Links

- [Official Website](https://silverbullet.md/)
- [Documentation](https://silverbullet.md/)
- [GitHub Repository](https://github.com/silverbulletmd/silverbullet)


## 🙏 Acknowledgments

- [SilverBullet](https://silverbullet.md/) by Zef Hemel
- [Logseq](https://logseq.com/) community for inspiration