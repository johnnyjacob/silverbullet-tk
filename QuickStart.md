# Quick Start

## Getting Started Checklist

- [ ] Start SilverBullet with Docker
- [ ] Install silversearcher plug
- [ ] Install treeview plug
- [ ] Add template blocks to your index page
- [ ] Start taking notes!


## Run

### Docker Run
```bash
docker run -d --restart unless-stopped \
  --name silverbullet \
  -p 3000:3000 \
  -v ./space:/space \
  -e SB_USER=user:password \
  ghcr.io/silverbulletmd/silverbullet:latest
```

Then access SilverBullet at: `http://localhost:3000`

### Essential Plugs

Install the following plugs to enhance your SilverBullet experience:
- **silversearcher** - Advanced search capabilities
- **treeview** - Visual folder navigation

#### How to Install Plugs

1. **Open the Library Manager**
   - Press `Cmd + /` (Mac) or `Ctrl + /` (Windows/Linux)
   - Type `Library: Manager` and press Enter

2. **Install the Plugs**
   - In the Library Manager, search for "silversearcher"
   - Click on it and select "Install"
   - Repeat for "treeview"

3. **Verify Installation**
   - Navigate to `PLUGS` page to see installed plugs
   - Or open command palette and type `Plugs: Update` to refresh

### Index Page Setup

Add these snippets to your index page for better overview:

**Recent Modifications:**

```template
${template.each(query[[
  from p = index.tag "page" 
  where p.name != "index" 
  order by p.lastModified desc 
  limit 20
]], template.new[==[[[${name}|${name.split("/").slice(1).join("-")}]], ]==])}
```

**Recent Tasks (limit 100):**
```template
${template.each(query[[
  from index.tag "task"
  where not _.done
  limit 100
]], templates.taskItem)}
```

**Filter Tasks by Attributes:**

Filter by tags:
```template
${template.each(query[[
  from index.tag "task"
  where not _.done and "important" in _.tags
  limit 100
]], templates.taskItem)}
```

Filter by due date:
```template
${template.each(query[[
  from index.tag "task"
  where not _.done and _.due
  order by _.due asc
  limit 100
]], templates.taskItem)}
```


**Pro Tip:** Press `Cmd/Ctrl + k` to quickly navigate between pages!