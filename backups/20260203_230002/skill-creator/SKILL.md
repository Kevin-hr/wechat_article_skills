---
name: skill-creator
description: Guide for creating effective skills. Use when creating/updating skills that extend Claude's capabilities with specialized knowledge, workflows, or tools.
---

# Skill Creator

## Core Principles

### Concise is Key

Context window is shared. Only add context Claude doesn't already have. Challenge each piece: "Does Claude need this?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

| Level | When to Use |
|-------|-------------|
| **High freedom** | Multiple valid approaches, context-dependent decisions |
| **Medium freedom** | Preferred pattern exists, some variation acceptable |
| **Low freedom** | Fragile operations, consistency critical |

## Quick Start

```bash
# 1. Initialize skill
scripts/init_skill.py <skill-name> --path <output>

# 2. Edit skill (add scripts, references, assets)
#    Update SKILL.md

# 3. Package
scripts/package_skill.py <path/to/skill-folder>
```

## Resources

| Topic | Reference |
|-------|-----------|
| Directory structure, components | [skill-anatomy.md](references/skill-anatomy.md) |
| Design patterns, progressive disclosure | [design-patterns.md](references/design-patterns.md) |
| 6-step creation process | [creation-process.md](references/creation-process.md) |

## Frontmatter Template

```yaml
---
name: skill-name
description: What the skill does AND when to use it. Include triggers/contexts.
---
```
