# Skill Creation Process

## 6 Steps

1. Understand with concrete examples
2. Plan reusable contents
3. Initialize the skill
4. Edit the skill
5. Package the skill
6. Iterate

---

## Step 1: Understand with Concrete Examples

**Questions to ask:**
- "What functionality should the skill support?"
- "Give examples of how this skill would be used?"
- "What would a user say to trigger this skill?"

**Example (image-editor skill):**
- "Remove red-eye from this image"
- "Rotate this image"
- Other use cases?

**Conclude** when functionality is clear.

---

## Step 2: Plan Reusable Contents

Analyze each example:

| Example | Script | Asset | Reference |
|---------|--------|-------|-----------|
| "Rotate this PDF" | `rotate_pdf.py` | - | - |
| "Build a todo app" | - | `hello-world/` template | - |
| "User login count" | - | - | `schema.md` |

---

## Step 3: Initialize the Skill

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script creates:
- Skill directory
- SKILL.md template with frontmatter
- `scripts/`, `references/`, `assets/` directories
- Example files

---

## Step 4: Edit the Skill

**Writing Guidelines:** Always use imperative/infinitive form.

### Frontmatter

```yaml
---
name: skill-name
description: What it does AND when to use it. Include triggers/contexts.
---
```

### Body

Write instructions for using the skill and bundled resources.

**Test scripts** by actually running them.

---

## Step 5: Package the Skill

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory:
```bash
scripts/package_skill.py <path> ./dist
```

**Packaging script validates:**
- YAML frontmatter format
- Skill naming conventions
- Description completeness
- File organization

Creates `.skill` file (zip format).

---

## Step 6: Iterate

**Workflow:**
1. Use skill on real tasks
2. Notice struggles/inefficiencies
3. Identify updates needed
4. Implement and test again
