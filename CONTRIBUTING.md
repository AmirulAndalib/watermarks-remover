# Contributing to watermarks-remover

Thanks for helping keep the skill accurate and the cleaners reliable. The
project is a small Python skill (`skills/remove-claude-marks/`) plus tests —
focused PRs land fastest.

## Who can do what

| Action | Who |
| --- | --- |
| Open issues | Anyone |
| Suggest a release | Anyone (use the **Release suggestion** issue template) |
| Open pull requests | Anyone (fork the repo) |
| Approve and merge pull requests | Maintainer only (`@guillaumemeyer`) |

`main` is protected. A change needs a pull request, a passing **CI** check
(`test`), and an approving review from the code owner before merge. Only the
maintainer can give that approval. Direct pushes to `main` are blocked for
non-admins.

To suggest a release without a code change: open a **Release suggestion**
issue.

## Prerequisites

- **Python 3.10+** (stdlib only for the skill scripts)
- From the repo root: `python3 -m pytest -q` should pass before you open a PR
- Optional for manual image checks: [`c2patool`](https://opensource.contentauthenticity.org/docs/c2patool/), [`exiftool`](https://exiftool.org/)

## Layout

| Path | Role |
| --- | --- |
| `skills/remove-claude-marks/SKILL.md` | Agent skill entry (workflow, ethics) |
| `skills/remove-claude-marks/scripts/` | Layer A text cleaners + image metadata strip |
| `skills/remove-claude-marks/references/` | Claude marks, removal matrix, ethics |
| `tests/` | Pytest suite and fixtures |
| `.github/workflows/ci.yml` | CI job `test` |

## Layers (what to change where)

1. **Layer A (Unicode / format controls)** — deterministic scripts under
   `scripts/` (`text_unicode.py`, `clean_text.py`, `inspect_text.py`). Prefer
   tests with fixtures in `tests/fixtures/`.
2. **Layer B (statistical rewrite)** — guidance in `SKILL.md` and references;
   no bundled model. Keep instructions clear and ethics-aware.
3. **Files (C2PA / EXIF / XMP / IPTC)** — `image_meta.py`, `clean_image.py`,
   `inspect_image.py`. Preserve image pixels; strip provenance metadata only.

## Checklist for a change

- [ ] Behaviour matches `SKILL.md` / `references/removal-matrix.md` when relevant
- [ ] Unit tests updated or added under `tests/`
- [ ] `python3 -m pytest -q` passes
- [ ] Docs updated (README and/or skill references) if user-facing behaviour
      changes
- [ ] No drive-by refactors unrelated to the fix or feature

## PR expectations

- Stay focused and match existing style (stdlib-first scripts, clear CLI flags)
- Do not commit secrets, private user files, or large binary fixtures unless
  needed and redacted
- Respect `references/ethics.md`: this tool is for content the user owns

Questions? Open an issue describing the input type (text / PNG / JPEG) and
which layer failed or is missing.

## Community

- [Code of Conduct](CODE_OF_CONDUCT.md) — expected behaviour in the project
- [Security policy](SECURITY.md) — how to report vulnerabilities privately
- [Bug report](.github/ISSUE_TEMPLATE/bug_report.md) and
  [feature request](.github/ISSUE_TEMPLATE/feature_request.md) templates
