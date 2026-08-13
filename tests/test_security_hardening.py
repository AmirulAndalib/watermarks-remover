"""Tests for the cleaners security hardening (safe argv, resource caps)."""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "remove-ai-marks" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from common import safe_arg  # noqa: E402
from container_meta import (  # noqa: E402
    MAX_ZIP_DECOMPRESSED_BYTES,
    _check_zip_budget,
    inspect_docx,
)


def test_safe_arg_prefixes_leading_dash():
    assert safe_arg("-@evil") == "./-@evil"
    assert safe_arg("--argfile") == "./--argfile"


def test_safe_arg_leaves_normal_paths_alone():
    assert safe_arg("photo.png") == "photo.png"
    assert safe_arg("dir/file.svg") == "dir/file.svg"
    assert safe_arg("/abs/path.pdf") == "/abs/path.pdf"
    assert safe_arg(".") == "."


def test_zip_budget_rejects_oversized_member():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", "<w:document/>")
    with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as zf:
        info = zf.infolist()[0]
    info.file_size = MAX_ZIP_DECOMPRESSED_BYTES + 1
    raised = False
    try:
        _check_zip_budget(info, [0])
    except ValueError:
        raised = True
    assert raised


def test_zip_budget_accumulates_across_members():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("a.xml", b"a")
        zf.writestr("b.xml", b"b")
    with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as zf:
        infos = zf.infolist()
    for info in infos:
        info.file_size = MAX_ZIP_DECOMPRESSED_BYTES // 2 + 1024
    budget = [0]
    raised = False
    for info in infos:
        try:
            _check_zip_budget(info, budget)
        except ValueError:
            raised = True
            break
    assert raised


def test_inspect_docx_with_ai_markers_does_not_crash():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("word/document.xml", "<w:document/>")
        zf.writestr(
            "docProps/app.xml",
            "<Properties><Application>Claude AI Writer</Application></Properties>",
        )
        zf.writestr(
            "docProps/core.xml",
            "<cp:coreProperties><dc:creator>Anthropic</dc:creator></cp:coreProperties>",
        )
    has_c2pa, has_ai, findings, _ = inspect_docx(buf.getvalue())
    assert has_ai
    assert findings
    assert not has_c2pa or has_ai