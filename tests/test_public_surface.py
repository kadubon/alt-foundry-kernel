from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from alt_foundry_kernel.cli import app
from alt_foundry_kernel.public_audit import run_public_audit

ROOT = Path(__file__).resolve().parents[1]


def _public_files() -> list[Path]:
    excluded_dirs = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
    }
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in excluded_dirs for part in path.parts):
            continue
        if path.name in {"uv.lock", ".coverage", "coverage.xml"}:
            continue
        if path.is_file():
            files.append(path)
    return files


def test_public_surface_has_no_local_paths_or_downloaded_paper_source() -> None:
    local_markers = [
        "C:" + "\\" + "Users",
        "C:" + "/" + "Users",
        "Desk" + "top",
        "Down" + "loads",
        "Abstraction Liquidity Theory" + ".tex",
    ]

    for path in _public_files():
        if path.name == "test_public_surface.py":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in local_markers:
            assert marker not in text, f"{marker!r} leaked in {path.relative_to(ROOT)}"


def test_japanese_readme_is_absent_and_public_docs_link_paper_doi() -> None:
    assert not (ROOT / "README.ja.md").exists()
    doi = "https://doi.org/10.5281/zenodo.20476200"
    docs = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
    assert all(doi in path.read_text(encoding="utf-8") for path in docs)
    assert "10.5281/zenodo.20476200" in (ROOT / "CITATION.cff").read_text(encoding="utf-8")


def test_no_local_env_files_or_obvious_secret_assignments() -> None:
    assert not [path for path in ROOT.rglob(".env*") if path.is_file()]

    secret_markers = [
        "BEGIN " + "PRIVATE KEY",
        "OPENAI_" + "API" + "_KEY=",
        "AWS_" + "SECRET_ACCESS_KEY",
        "api" + "_key =",
        "token" + " =",
    ]
    for path in _public_files():
        if path.name in {".gitignore", "test_public_surface.py"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in secret_markers:
            assert marker not in text, f"secret-like marker leaked in {path.relative_to(ROOT)}"


def test_no_fake_public_repository_urls_are_present() -> None:
    fake_markers = [
        "github.com/" + "alt-foundry-kernel/alt-foundry-kernel",
        "alt-foundry-kernel" + ".example",
    ]
    for path in _public_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in fake_markers:
            assert marker not in text, f"placeholder URL leaked in {path.relative_to(ROOT)}"


def test_public_audit_strict_passes_on_public_surface() -> None:
    report = run_public_audit(ROOT, strict=True)

    assert report.ok, [finding for finding in report.findings if finding.severity == "error"]

    result = CliRunner().invoke(app, ["audit-public", "--strict", "--root", str(ROOT)])

    assert result.exit_code == 0, result.output
