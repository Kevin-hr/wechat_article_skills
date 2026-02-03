# Skill Anatomy

目录结构、组件说明、资源类型。

## Directory Structure

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code
    ├── references/       - Documentation loaded as needed
    └── assets/           - Files used in output
```

## SKILL.md Components

| Component | Required | Description |
|-----------|----------|-------------|
| Frontmatter | Yes | YAML with `name` and `description` |
| Body | Yes | Markdown instructions |

### Frontmatter

- `name`: The skill identifier
- `description`: Primary triggering mechanism - include what it does AND when to use it

### Body

Instructions and guidance. Only loaded AFTER skill triggers.

## Bundled Resources

### Scripts (`scripts/`)

**When to include:**
- Same code rewritten repeatedly
- Deterministic reliability needed

**Example:** `scripts/rotate_pdf.py`

**Benefits:** Token efficient, deterministic, executable without context

### References (`references/`)

**When to include:**
- Documentation Claude should reference while working
- Database schemas, API docs, domain knowledge

**Best practice:** Large files (>10k words) should include grep search patterns

**Avoid duplication:** Info in SKILL.md OR references, not both

### Assets (`assets/`)

**When to include:**
- Files used in final output (templates, icons, fonts)

**Example:** `assets/logo.png`, `assets/template.pptx`

## What NOT to Include

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- Any auxilary documentation

Skills should only contain what's needed for the task.
