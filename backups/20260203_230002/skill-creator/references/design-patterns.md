# Progressive Disclosure Patterns

## Three-Level Loading

1. **Metadata** (~100 words) - Always in context
2. **SKILL.md body** (<5k words) - When skill triggers
3. **Bundled resources** - Unlimited (scripts executable without context)

## Pattern 1: High-Level Guide with References

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md)
- **API reference**: See [REFERENCE.md](REFERENCE.md)
- **Examples**: See [EXAMPLES.md](EXAMPLES.md)
```

Claude loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

## Pattern 2: Domain-Specific Organization

```
bigquery-skill/
├── SKILL.md (overview + navigation)
└── reference/
    ├── finance.md
    ├── sales.md
    ├── product.md
    └── marketing.md
```

When user asks about sales metrics → Claude reads sales.md only.

Similarly for frameworks:
```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

## Pattern 3: Conditional Details

```markdown
# DOCX Processing

## Creating documents

Use docx-js. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify XML directly.

**Tracked changes**: See [REDLINING.md](REDLINING.md)
**OOXML details**: See [OOXML.md](OOXML.md)
```

## Guidelines

- **Avoid deeply nested references** - Keep one level deep
- **Structure long files** - Include TOC for files >100 lines
- **Keep SKILL.md lean** - Move details to references
