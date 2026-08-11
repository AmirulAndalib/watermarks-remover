```
_ _ _ ____ ___ ____ ____ _  _ ____ ____ _  _ ____    ____ ____ _  _ ____ _  _ ____ ____
| | | |__|  |  |___ |__/ |\/| |__| |__/ |_/  [__  __ |__/ |___ |\/| |  | |  | |___ |__/
|_|_| |  |  |  |___ |  \ |  | |  | |  \ | \_ ___]    |  \ |___ |  | |__|  \/  |___ |  \
```

# watermarks-remover

<!-- logo: figlet -d .figlet -f cybermedium -w 120 "watermarks-remover" -->

[![CI](https://github.com/guillaumemeyer/watermarks-remover/actions/workflows/ci.yml/badge.svg)](https://github.com/guillaumemeyer/watermarks-remover/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/guillaumemeyer/watermarks-remover)](https://github.com/guillaumemeyer/watermarks-remover/releases)

Agent skill + stdlib Python scripts to strip **multi-vendor AI provenance marks** from text and files — for privacy and hygiene on content **you own**.

| Layer | Target | How |
| --- | --- | --- |
| **A** | Invisible Unicode, exotic spaces, bidi, tag chars | Deterministic Python scripts |
| **B** | Statistical (token-sampling) text watermarks | Agent rewrite + optional `rewrite_text.py` hook |
| **Files** | C2PA / EXIF / XMP / doc props | PNG, JPEG, SVG, PDF, DOCX, ODT, HTML, Markdown |

Vendors / ecosystems (class-level): **Claude**, **Gemini / SynthID-Text**, **OpenAI** provenance surfaces, **open-LLM** Kirchenbauer-style marks.

**Latest release:** [v0.0.1](https://github.com/guillaumemeyer/watermarks-remover/releases/tag/v0.0.1)

Skill path: [`skills/remove-ai-marks/`](skills/remove-ai-marks/)  
(migration: formerly `remove-claude-marks`; slash alias `/remove-claude-marks` still documented)

## Install (agent skill)

```bash
# Grok Build / project-local
mkdir -p .grok/skills
ln -sfn "$(pwd)/skills/remove-ai-marks" .grok/skills/remove-ai-marks

# User-global Grok
mkdir -p ~/.grok/skills
ln -sfn "$(pwd)/skills/remove-ai-marks" ~/.grok/skills/remove-ai-marks
```

Invoke with `/remove-ai-marks` or ask to “strip AI watermarks / C2PA / Claude marks / SynthID-class text.”

Optional system tools (auto-used when present):

| Tool | Role |
| --- | --- |
| [`c2patool`](https://opensource.contentauthenticity.org/docs/c2patool/) | Inspect C2PA manifests |
| [`exiftool`](https://exiftool.org/) | Residual metadata strip (esp. **PDF**) |

Core scripts need **Python 3.10+** stdlib only. Layer B model calls are optional.

## Quick use (scripts)

```bash
SCRIPTS=skills/remove-ai-marks/scripts

# Unified inspect / clean
python3 "$SCRIPTS/inspect_file.py" draft.md
python3 "$SCRIPTS/clean_file.py" draft.md -o draft.cleaned.md
python3 "$SCRIPTS/clean_file.py" photo.png -o photo.cleaned.png
python3 "$SCRIPTS/clean_file.py" notes.docx -o notes.cleaned.docx

# Text Layer A
python3 "$SCRIPTS/inspect_text.py" draft.md
python3 "$SCRIPTS/clean_text.py" draft.md -o draft.cleaned.md --stats

# Layer B rewrite hook (default: print prompt only — no model required)
python3 "$SCRIPTS/rewrite_text.py" draft.md --backend print-prompt --strength paraphrase
# Optional local Ollama:
# WATERMARKS_REWRITE_BACKEND=ollama WATERMARKS_REWRITE_MODEL=llama3.2 \
#   python3 "$SCRIPTS/rewrite_text.py" draft.md -o draft.rewritten.md

# Images
python3 "$SCRIPTS/inspect_image.py" shot.png
python3 "$SCRIPTS/clean_image.py" shot.png -o shot.cleaned.png
```

## Coverage matrix

| Channel | Claude | Gemini/SynthID | OpenAI | Open-LLM |
| --- | --- | --- | --- | --- |
| Unicode / edit-based text | Layer A | Layer A | Layer A | Layer A |
| Statistical sampling text | Layer B best-effort | Layer B best-effort | Layer B if present | Layer B best-effort |
| C2PA / file metadata | Yes (listed formats) | Yes when present | Yes when present | Yes when present |
| Pixel image marks | Out of scope | Out of scope | Out of scope | Out of scope |
| Training backdoors | Out of scope | Out of scope | Out of scope | Out of scope |

Details: [`skills/remove-ai-marks/references/vendor-notes.md`](skills/remove-ai-marks/references/vendor-notes.md), [`mark-classes.md`](skills/remove-ai-marks/references/mark-classes.md).

---

## How text marking works (short)

Modern LLM watermarks often hide a signal in **which tokens are chosen** (generative / sampling bias), not only in invisible characters. Edit-based schemes inject Unicode or synonym rules. File schemes attach **C2PA** or generator metadata.

- **Layer A** removes edit-based Unicode carriers (testable).
- **Layer B** attacks sampling watermarks via heavy rewrite (best-effort; literature-standard attacks such as paraphrase / back-translation).
- **File cleaners** strip C2PA/XMP/props from supported containers.

Until vendors ship public detectors and keys, **no tool can honestly certify** “this fails the official check.” Reports must separate verifiable vs best-effort work.

Prefer a **non-origin** model for Layer B (do not rewrite Claude text with Claude if you are trying to avoid re-stamping).

---

## File formats

| Format | Inspect | Clean |
| --- | --- | --- |
| PNG / JPEG | C2PA chunks / APP11, AI XMP hints | Drop metadata segments |
| SVG | `<metadata>`, XMP | Strip blocks |
| PDF | Byte/XMP + optional tools | **exiftool** preferred; degraded without it |
| DOCX | docProps / customXml | Scrub props, drop customXml |
| ODT | meta.xml | Drop generator / AI-ish meta |
| HTML | meta, JSON-LD, data-ai* | Strip tags/attrs |
| Markdown | YAML frontmatter AI keys | Drop keys + Layer A body |

Pixel-domain watermarks remain out of scope.

---

## Removal options (summary)

| Option | Removes | Notes |
| --- | --- | --- |
| Unicode scrub (Layer A) | ZWSP, bidi, tags, exotic spaces, … | Safe default for text |
| Rewrite (Layer B) | Statistical token marks (best-effort) | Always offered by skill |
| Container/metadata strip | File provenance | See format table |
| Open-weight local models | Avoid re-stamping with origin model | Operational alternative |

Matrix: [`skills/remove-ai-marks/references/removal-matrix.md`](skills/remove-ai-marks/references/removal-matrix.md).

## Ethics

See [`skills/remove-ai-marks/references/ethics.md`](skills/remove-ai-marks/references/ethics.md). For privacy and research on **your** content — not academic fraud or false “human-written” claims.

## Tests

```bash
python3 -m venv .venv && .venv/bin/pip install pytest
.venv/bin/python -m pytest tests/ -q
```

## Changelog

### [v0.0.1](https://github.com/guillaumemeyer/watermarks-remover/releases/tag/v0.0.1) — initial multi-vendor release

- Agent skill `remove-ai-marks` (replaces Claude-only `remove-claude-marks`)
- **Layer A:** invisible Unicode / bidi / tag chars / space homoglyphs (`inspect_text` / `clean_text`)
- **Layer B:** rewrite guidance + optional `rewrite_text.py` (print-prompt, Ollama, OpenAI-compatible)
- **Files:** C2PA/AI metadata strip for PNG, JPEG, SVG, PDF, DOCX, ODT, HTML, Markdown
- Unified `inspect_file.py` / `clean_file.py`
- Multi-vendor docs (Claude, Gemini/SynthID-class, OpenAI, open-LLM)
- Stdlib-first scripts; optional `c2patool` / `exiftool`

## License

MIT — see [LICENSE](LICENSE).

## References

- [How Claude marks AI-generated content](https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content) (Anthropic)
- Dathathri et al., [*Scalable watermarking for identifying large language model outputs*](https://www.nature.com/articles/s41586-024-08025-4) (SynthID-Text, Nature 2024)
- [C2PA](https://c2pa.org/) / [c2patool](https://opensource.contentauthenticity.org/docs/c2patool/)
- Kirchenbauer et al., [*A Watermark for Large Language Models*](https://arxiv.org/abs/2301.10226)
- [google-deepmind/synthid-text](https://github.com/google-deepmind/synthid-text) (research reference; not used for detection here)
