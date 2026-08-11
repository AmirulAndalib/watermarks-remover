# Removal matrix

| Target | Method | Script / action | Side effects | Verifiable today? |
| --- | --- | --- | --- | --- |
| Invisible Unicode / exotic spaces | Strip / normalize | `inspect_text.py`, `clean_text.py` | Minimal | Yes (codepoint report) |
| Statistical text watermark | Paraphrase / back-translate / structural rewrite | Agent Layer B (always offer) | Meaning/style drift | No official Claude detector yet |
| C2PA Content Credentials | Drop APP11 / text chunks / exiftool | `inspect_image.py`, `clean_image.py` | Loses provenance metadata | Yes (`c2patool` / re-inspect) |
| EXIF / XMP / IPTC AI tags | Full metadata strip | `clean_image.py` (default) | Loses camera/title metadata | Yes |
| Residual C2PA after soft strip | Re-encode / convert | Pillow/ImageMagick (manual) | Possible quality loss | Yes |

## Default pipeline

1. **Inspect** (text and/or image).
2. **Layer A** clean text; **file** clean images.
3. **Always offer Layer B** rewrite for prose (paraphrase → back-translate → outline regen).
4. Prefer a **non-Claude** rewrite model when available (avoid re-stamping).
5. Report: Layer B is best-effort until Anthropic ships public detection.

## Code vs prose

- **Prose / Markdown:** full A + B.
- **Code:** Layer A + formatter (`prettier`, `black`, etc.); statistical marks are weak; light rewrite only with user OK (risk of breakage).
