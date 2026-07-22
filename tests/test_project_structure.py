"""Regression tests for the initial Lead Hunting MVP scaffold."""

from pathlib import Path
import unittest


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
