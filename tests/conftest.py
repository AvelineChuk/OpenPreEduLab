"""Shared fixtures for software validation with the synthetic sample dataset."""

from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_dataset_path() -> Path:
    """Return the repository's synthetic city-year sample dataset path."""
    return PROJECT_ROOT / "datasets" / "sample_preschool_data.csv"


@pytest.fixture
def sample_inclusive_dataset_path() -> Path:
    """Return the synthetic institution-level inclusive research dataset."""
    return PROJECT_ROOT / "datasets" / "sample_inclusive_data.csv"
