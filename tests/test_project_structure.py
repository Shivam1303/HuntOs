"""Regression tests for the initial Lead Hunting MVP scaffold."""

import tomllib
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProjectStructureTests(unittest.TestCase):
    """Keep the initial dependency-oriented package layout intact."""

    def test_required_packages_exist(self) -> None:
        expected_packages = (
            "core",
            "core/config",
            "core/database",
            "core/llm",
            "modules",
            "modules/opportunities",
            "modules/scoring",
            "modules/research",
            "modules/proposals",
            "api",
        )

        for package in expected_packages:
            package_path = PROJECT_ROOT / package
            self.assertTrue(package_path.is_dir(), package)
            self.assertTrue((package_path / "__init__.py").is_file(), package)

    def test_review_frontend_and_tests_directories_exist(self) -> None:
        self.assertTrue((PROJECT_ROOT / "frontend").is_dir())
        self.assertTrue((PROJECT_ROOT / "tests").is_dir())

    def test_out_of_scope_module_directories_are_absent(self) -> None:
        forbidden_directories = (
            "crm",
            "outreach",
            "analytics",
            "learning",
            "scheduler",
            "multi_agent",
        )

        for directory in forbidden_directories:
            self.assertFalse((PROJECT_ROOT / "modules" / directory).exists(), directory)

    def test_pyproject_declares_python_and_package_roots(self) -> None:
        pyproject_path = PROJECT_ROOT / "pyproject.toml"

        with pyproject_path.open("rb") as pyproject_file:
            configuration = tomllib.load(pyproject_file)

        self.assertEqual(configuration["project"]["name"], "lead-hunting-mvp")
        self.assertEqual(configuration["project"]["requires-python"], ">=3.12")
        self.assertEqual(
            configuration["build-system"]["build-backend"], "setuptools.build_meta"
        )
        self.assertEqual(
            configuration["tool"]["setuptools"]["packages"]["find"]["include"],
            ["core*", "modules*", "api*"],
        )

    def test_pyproject_configures_test_lint_and_type_checking_tools(self) -> None:
        with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
            configuration = tomllib.load(pyproject_file)

        tool_configuration = configuration["tool"]
        self.assertEqual(
            tool_configuration["pytest"]["ini_options"]["testpaths"], ["tests"]
        )
        self.assertEqual(tool_configuration["ruff"]["target-version"], "py312")
        self.assertEqual(tool_configuration["ruff"]["lint"]["select"], ["E", "F", "I"])
        self.assertEqual(tool_configuration["mypy"]["python_version"], "3.12")
        self.assertTrue(tool_configuration["mypy"]["strict"])

    def test_environment_template_has_no_embedded_gemini_key(self) -> None:
        environment_template = (PROJECT_ROOT / ".env.example").read_text()
        environment_values = {
            line.partition("=")[0]: line.partition("=")[2]
            for line in environment_template.splitlines()
            if line and not line.startswith("#")
        }

        self.assertEqual(environment_values["GEMINI_API_KEY"], "")
        self.assertEqual(
            environment_values["DATABASE_URL"],
            "postgresql+psycopg://hunter:hunter@localhost:5432/hunter",
        )
