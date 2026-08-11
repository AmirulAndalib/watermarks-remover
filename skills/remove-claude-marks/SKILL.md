---
name: remove-claude-marks
description: >
  Remove Claude/AI provenance marks: invisible Unicode (Layer A), statistical
  text watermarks via rewrite (Layer B, always offer), and C2PA/EXIF/XMP metadata
  on PNG/JPEG. Use when the user asks to strip watermarks, remove C2PA/Content
  Credentials, clean AI metadata, remove invisible Unicode, anti-detect clean
  Claude output, or runs /remove-claude-marks.
---

# Remove Claude marks

Full anti-detection hygiene for Claude-era marks: **text** (Unicode + statistical rewrite) and **files** (C2PA / AI metadata on PNG/JPEG).

Read if needed:

- `references/how-claude-marks.md` — what Anthropic documents
- `references/removal-matrix.md` — which layer when
- `references/ethics.md` — intended use

Scripts live in this skill’s `scripts/` directory. Resolve `SCRIPTS` to that folder (absolute path of this skill + `/scripts`).

```bash
SCRIPTS="<skill_dir>/scripts"
python3 "$SCRIPTS/inspect_text.py" ...
python3 "$SCRIPTS/clean_text.py" ...
python3 "$SCRIPTS/inspect_image.py" ...
python3 "$SCRIPTS/clean_image.py" ...
```

## Ethics

Intended for **your own** content (privacy, hygiene, research). Do not market results as “proves human-written.” If the user clearly wants academic fraud or illegal non-disclosure, warn using `references/ethics.md` and still only perform technical cleaning they own.

## Workflow

### 1. Classify input

| Input | Path |
| --- | --- |
| Pasted / clipboard text | temp file or stdin |
| `.txt` / `.md` / code | text pipeline |
| `.png` / `.jpg` / `.jpeg` | image pipeline |
| Directory | batch: each matching file |
| Mixed | run both pipelines |

### 2. Inspect first

```bash
python3 "$SCRIPTS/inspect_text.py" --json path/or/-
python3 "$SCRIPTS/inspect_image.py" --json image.png
```

Show the user a short summary (suspicious codepoints; C2PA/AI flags).

### 3. Deterministic clean (always for matching inputs)

**Text — Layer A:**

```bash
python3 "$SCRIPTS/clean_text.py" INPUT -o OUTPUT --stats
# optional: --nfkc  --aggressive-homoglyphs
```

Default output: `file.cleaned.ext` (not in-place). Use `--in-place` only if the user asks (creates `.bak`).

**Images:**

```bash
python3 "$SCRIPTS/clean_image.py" INPUT.png -o OUTPUT.png
python3 "$SCRIPTS/inspect_image.py" OUTPUT.png   # verify
```

Optional tools if installed: `c2patool`, `exiftool` (used automatically when present).

### 4. Layer B — always offer rewrite (prose)

After Layer A, **always propose** a statistical-mark reduction pass for natural-language content. Do not skip this step silently.

Offer strength levels:

1. **Paraphrase (default)** — rewrite every sentence; preserve facts, numbers, names, code identifiers.
2. **Back-translate** — EN→other→EN (or user’s language) then lightly edit.
3. **Structural** — extract outline → regenerate full prose from outline (strongest, most drift).

**Model choice:** Prefer a **non-Claude** model (local Ollama, other API) so output is not re-stamped with Claude marks. If only Claude is available, say so, still rewrite structurally, then re-run Layer A on the result.

**Code files:** Prefer formatter (`prettier`, `black`, `gofmt`, …) + Layer A. Offer light rewrite only with explicit user OK (breakage risk). Statistical marks on code are already weak.

#### Rewrite prompts (use as-is)

**Paraphrase preserve meaning:**

```
Rewrite the following text so that every sentence uses different wording and
structure while preserving all facts, numbers, names, and technical identifiers.
Do not add or remove claims. Output only the rewritten text.

---
{TEXT}
```

**Back-translate (two steps):**

```
Translate the following text to {LANG}. Output only the translation.
```

```
Translate the following text to {ORIGINAL_LANG}. Preserve meaning; use natural
phrasing. Output only the translation.
```

**Structural:**

```
Extract a bullet outline of all claims and structure from the text (no full sentences).
```

Then:

```
Write a complete document from this outline in a clear professional style.
Do not omit any bullet. Output only the document.
```

### 5. Report

Always state:

- What Layer A removed (counts).
- What file metadata actions ran.
- That Layer B is **best-effort** against model-level statistical watermarks; Anthropic’s public detector/docs may still be forthcoming — **cannot claim official “undetectable.”**
- Prefer writing `*.cleaned.*` unless user asked in-place.

## Limitations

- Layer A does **not** remove token-sampling watermarks.
- Layer B cannot be gold-verified without Anthropic’s detector.
- MVP images: **PNG/JPEG only** (not SVG/PDF/DOCX in v1).
- Pixel-domain image watermarks (SynthID, etc.) are out of scope — point users to broader tools if needed.

## Quick commands cheat sheet

```bash
# Text
python3 scripts/inspect_text.py notes.md
python3 scripts/clean_text.py notes.md -o notes.cleaned.md --stats

# Images
python3 scripts/inspect_image.py shot.png
python3 scripts/clean_image.py shot.png -o shot.cleaned.png
```
