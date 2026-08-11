# Mark classes

## 1. Edit-based text (Unicode / rules)

Invisible or near-invisible characters, exotic spaces, bidi controls, tag characters, synonym tables.

| Inspect kinds (Layer A) | Examples |
| --- | --- |
| `zwj_family` | ZWSP, ZWNJ, ZWJ, WJ, BOM |
| `bidi` | LRE/RLO/LRI/… |
| `tag_chars` | U+E0001–U+E007F |
| `variation_selector` | VS1–VS256 |
| `space` | NBSP, em space, ideographic space |
| `confusable` | Cyrillic/fullwidth Latin (aggressive) |

**Removal:** `clean_text.py` / Layer A — deterministic, verifiable.

Maps to Nature paper “edit-based watermarking.”

## 2. Generative / statistical text (token sampling)

Bias next-token sampling toward a pseudo-random green list / score (Kirchenbauer, SynthID-Text / Tournament sampling, etc.). Signal lives in **word choice**, not metadata.

**Removal:** Layer B rewrite (paraphrase → back-translate → structural). Best-effort; no gold cert without vendor detector/key.

Maps to Nature paper primary method (SynthID-Text).

## 3. Data-driven / backdoor

Model trained or fine-tuned so trigger prompts produce marked or identifiable behavior.

**Out of scope** for this skill (model-side).

## 4. File provenance metadata (C2PA / EXIF / XMP / props)

Signed Content Credentials and AI generator tags in containers.

| Format | Support |
| --- | --- |
| PNG / JPEG | Full strip (stdlib + optional exiftool) |
| SVG | Drop metadata/XMP blocks |
| PDF | Prefer exiftool; degraded stdlib XMP strip |
| DOCX / ODT | Scrub zip XML props / customXml |
| HTML | Meta generator / JSON-LD / data-ai* |
| Markdown | YAML frontmatter AI keys |

**Removal:** `clean_file.py` / `clean_image.py` — usually verifiable by re-inspect.

## 5. Pixel-domain image watermarks

Invisible image marks (e.g. SynthID for images). **Out of scope.**
