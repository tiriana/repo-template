"""Placeholder smoke test: replace it with tests for real behaviour."""

import importlib.metadata

import your_project_name


def test_package_is_importable() -> None:
    assert your_project_name.__name__ == "your_project_name"


def test_distribution_reports_a_version() -> None:
    version = importlib.metadata.version("your-project-name")
    assert version and version != "UNKNOWN"
