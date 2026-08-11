```
_ _ _ ____ ___ ____ ____ _  _ ____ ____ _  _ ____    ____ ____ _  _ ____ _  _ ____ ____
| | | |__|  |  |___ |__/ |\/| |__| |__/ |_/  [__  __ |__/ |___ |\/| |  | |  | |___ |__/
|_|_| |  |  |  |___ |  \ |  | |  | |  \ | \_ ___]    |  \ |___ |  | |__|  \/  |___ |  \
```

# watermarks-remover

<!-- logo: figlet -d .figlet -f cybermedium -w 120 "watermarks-remover" -->

Agent skill to strip **Claude / AI provenance marks** from text and images:

| Layer | Target | How |
| --- | --- | --- |
| **A** | Invisible Unicode, exotic spaces, format controls | Deterministic Python scripts |
| **B** | Statistical (token-sampling) text watermarks | Agent-orchestrated rewrite (always offered) |
| **Files** | C2PA Content Credentials + EXIF/XMP/IPTC AI tags | PNG/JPEG metadata strip |

Skill path: [`skills/remove-claude-marks/`](skills/remove-claude-marks/).

## Install (agent skill)

Copy or symlink the skill into your agent’s skills directory:

```bash
# Grok Build / project-local
mkdir -p .grok/skills
ln -s "$(pwd)/skills/remove-claude-marks" .grok/skills/remove-claude-marks

# User-global Grok
mkdir -p ~/.grok/skills
ln -s "$(pwd)/skills/remove-claude-marks" ~/.grok/skills/remove-claude-marks
```

Then invoke with `/remove-claude-marks` or ask to “strip Claude watermarks / C2PA / AI metadata.”

Optional system tools (auto-used when present):

- [`c2patool`](https://opensource.contentauthenticity.org/docs/c2patool/) — inspect C2PA manifests
- [`exiftool`](https://exiftool.org/) — residual metadata strip

Core scripts need **Python 3.10+** stdlib only.

## Quick use (scripts)

```bash
SCRIPTS=skills/remove-claude-marks/scripts

# Text Layer A
python3 "$SCRIPTS/inspect_text.py" draft.md
python3 "$SCRIPTS/clean_text.py" draft.md -o draft.cleaned.md --stats

# Images
python3 "$SCRIPTS/inspect_image.py" image.png
python3 "$SCRIPTS/clean_image.py" image.png -o image.cleaned.png
```

Layer B (rewrite) is driven by the agent following `SKILL.md` — not a bundled model.

---

## How Claude marks content

Anthropic documents two complementary systems under the EU AI Act Article 50(2) transparency code ([official article](https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content)):

1. **Embedded text watermarks** — woven into generated text at the **model level** (imperceptible; survives copy-paste).
2. **Signed C2PA provenance metadata** on supported files (examples: `.png`, `.jpg`, `.svg`).

Models launched on/after **2026-08-02** support marking at launch; older models are in transition. Marks apply **worldwide** across Claude surfaces (API, chat, Claude Code, etc.). Detection APIs for third parties are described as forthcoming.

Important Anthropic caveats:

- A detected mark means content **may have been processed** by Claude — not proof Claude originated the ideas.
- Absence of a mark does **not** prove human-only origin.
- Proofreading, translation, and summarization can stamp human-written material.

---

## Statistical token-sampling watermarks

This chapter is the mental model for **Layer B**. Anthropic has **not** published Claude’s exact algorithm; the following is the standard technical class of “imperceptible text watermarks woven into the text itself,” used by systems such as Google’s SynthID-Text and the Kirchenbauer et al. line of LLM watermarks.

### Why text is hard to watermark

Images have noise you can hide bits in. Plain text is sparse: almost any change is visible to a reader. You cannot reliably hide a classic payload in “extra pixels.” So modern LLM watermarks hide a signal in **which words the model chooses**, not in invisible ink alone.

### How token sampling works

An LLM does not emit a finished essay in one shot. At each step it produces a **distribution over the next token** (a vocabulary of tens of thousands of pieces of words). A sampler then picks one token — randomly among likely options when temperature &gt; 0, or the top token when greedy.

Those near-ties are the watermark channel.

### The bias trick

A secret key and a hash of the recent context define a pseudo-random partition (or score) of the vocabulary — often “green list” vs “red list,” or a continuous SynthID-style score.

When generating, the sampler **nudges** probability mass toward green / high-score tokens among options that were already plausible. Human readers still see fluent text; over a **long enough** passage, green tokens appear more often than chance.

Detection re-tokenizes the text, recomputes the same scores with the key, and tests whether the aggregate score is suspiciously high. Short snippets lack statistical power (Anthropic also notes short text is unreliable to mark).

```
context → hash(key, context) → green/red (or scores)
model logits → bias toward green → sample token → append → repeat
```

### What this is *not*

| Myth | Reality |
| --- | --- |
| “Claude only inserts zero-width characters” | Zero-width / homoglyph tricks exist in the wild and are worth scrubbing (**Layer A**), but Anthropic’s description of marks *woven into text at the model level* matches **sampling bias**, not metadata or only ZWSP. |
| “Paste into Notepad removes it” | Statistical marks live in **word choice**. Plain-text paste keeps the words. |
| “Deleting EXIF removes text marks” | File metadata is a separate channel (C2PA). Text marks travel in the characters of the prose. |
| “One synonym swap is enough” | Detection is statistical over many tokens. Light edits may leave the signal; **heavy paraphrase** is the literature-standard attack. |

### How removal works (and limits)

| Approach | Why it can work | Cost |
| --- | --- | --- |
| **Paraphrase** (another model or human) | Changes the token sequence; green-list bias no longer concentrates | Style/meaning drift |
| **Back-translation** | Classic attack: round-trip through another language reshuffles tokens | Idiom drift |
| **Structural rewrite** (outline → regenerate) | Maximally breaks n-gram / dependency structure of the mark | Highest drift |
| **Very short text** | Below detection threshold | Not a strategy for long docs |
| **Code formatters** | Code has low entropy; formatters rewrite whitespace/tokens | Limited to code |

Until Anthropic ships public detectors and algorithm details, **no tool can honestly certify** “this will fail Claude’s official check.” Layer B is **best-effort** using known attacks on the watermark *class*.

### Prefer non-Claude rewriters

If you paraphrase **with Claude**, a marked model may **re-apply** a watermark. Prefer local open-weight models or another provider for Layer B when possible; then run Layer A again on the result.

### Relation to Layer A in this repo

- **Layer A** (`inspect_text.py` / `clean_text.py`): removes invisible code points, exotic spaces, optional confusables — fully testable, no model required.
- **Layer B** (skill-orchestrated rewrite): targets statistical sampling marks — always **offered** by the skill after Layer A for prose.

Both are required for a full anti-detection pass on text.

---

## File marks (C2PA)

For images, Claude may attach **signed C2PA Content Credentials**. Those live in container metadata (e.g. JPEG APP11 / JUMBF, PNG ancillary chunks, XMP), not in pixel art necessarily.

They are **tamper-evident while present** and **easy to strip** (this skill, ExifTool, re-encode, many social re-uploads). Stripping removes the provenance signal; it does not rewrite pixels for invisible image watermarks (out of scope here).

```bash
python3 skills/remove-claude-marks/scripts/inspect_image.py photo.jpg
python3 skills/remove-claude-marks/scripts/clean_image.py photo.jpg -o photo.cleaned.jpg
```

---

## Removal options (summary)

| Option | Removes | Notes |
| --- | --- | --- |
| Unicode scrub (Layer A) | ZWSP, bidi marks, soft hyphens, exotic spaces, … | Safe default for text |
| Paraphrase / back-translate (Layer B) | Statistical token marks (best-effort) | Always offered by skill |
| C2PA/metadata strip | File provenance | PNG/JPEG MVP |
| Open-weight models | Avoid Claude marks entirely | Operational alternative |
| Don’t AI-touch final copy | Avoid accidental re-stamp | Proofreading also marks |

Details: [`skills/remove-claude-marks/references/removal-matrix.md`](skills/remove-claude-marks/references/removal-matrix.md).

## Ethics

See [`skills/remove-claude-marks/references/ethics.md`](skills/remove-claude-marks/references/ethics.md). For privacy and research on **your** content — not academic fraud or false “human-written” claims.

## Tests

```bash
python3 -m venv .venv && .venv/bin/pip install pytest
.venv/bin/python -m pytest tests/ -q
```

## License

MIT — see [LICENSE](LICENSE).

## References

- [How Claude marks AI-generated content](https://support.claude.com/en/articles/16266773-how-claude-marks-ai-generated-content) (Anthropic)
- [C2PA](https://c2pa.org/) / [c2patool](https://opensource.contentauthenticity.org/docs/c2patool/)
- Kirchenbauer et al., [*A Watermark for Large Language Models*](https://arxiv.org/abs/2301.10226); DeepMind SynthID-Text
- Adjacent image tooling: [remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks), [C2PAremover](https://github.com/ngmisl/C2PAremover)
- Hosted text-only rewrite tool (Layer B style; no C2PA/Unicode): [claudewatermarkremover.app](https://claudewatermarkremover.app/)
