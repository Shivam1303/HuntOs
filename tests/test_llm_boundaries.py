"""Architecture guards for provider independence."""

import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_business_modules_do_not_import_google_sdk() -> None:
    for source_file in (PROJECT_ROOT / "modules").rglob("*.py"):
        source = source_file.read_text()
        assert "google.genai" not in source, source_file
        assert "from google import genai" not in source, source_file


def test_only_gemini_adapter_imports_google_sdk() -> None:
    direct_importers: list[Path] = []
    for package in ("api", "core", "modules"):
        for source_file in (PROJECT_ROOT / package).rglob("*.py"):
            source = source_file.read_text()
            if "google.genai" in source or "from google import genai" in source:
                direct_importers.append(source_file.relative_to(PROJECT_ROOT))

    assert direct_importers == [Path("core/llm/gemini.py")]


def test_project_uses_current_google_genai_package_only() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        configuration = tomllib.load(pyproject_file)

    dependencies = configuration["project"]["dependencies"]
    assert any(item.startswith("google-genai>=") for item in dependencies)
    assert all(not item.startswith("google-generativeai") for item in dependencies)
