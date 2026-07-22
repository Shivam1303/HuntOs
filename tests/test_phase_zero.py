"""Tests for the remaining Phase 0 project setup contracts."""

from pathlib import Path
from unittest import TestCase

from fastapi.testclient import TestClient

from api.main import app

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class PhaseZeroTests(TestCase):
    """Verify the minimal API and ignored local-development artifacts."""

    def test_health_endpoint_returns_success(self) -> None:
        response = TestClient(app).get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_gitignore_excludes_local_artifacts_and_secrets(self) -> None:
        ignored_patterns = (PROJECT_ROOT / ".gitignore").read_text().splitlines()

        self.assertIn(".env", ignored_patterns)
        self.assertIn("__pycache__/", ignored_patterns)
        self.assertIn(".venv/", ignored_patterns)
        self.assertIn("*.db", ignored_patterns)
