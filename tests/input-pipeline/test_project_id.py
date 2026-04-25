#!/usr/bin/env python3
"""Tests for sequential project ID allocation."""

import pytest
from pathlib import Path
import sys
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib" / "input-pipeline"))

from project_id_allocator import ProjectIdAllocator


@pytest.fixture
def temp_proyectos():
    """Create temporary proyectos directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    proyectos_dir = temp_dir / "proyectos"
    proyectos_dir.mkdir()
    yield proyectos_dir
    shutil.rmtree(temp_dir)


def test_allocate_first_id(temp_proyectos):
    """Test allocating first ID when no projects exist."""
    allocator = ProjectIdAllocator(temp_proyectos)
    next_id = allocator.allocate_next_id()
    assert next_id == 1


def test_allocate_sequential(temp_proyectos):
    """Test sequential ID allocation."""
    allocator = ProjectIdAllocator(temp_proyectos)

    # Create projects 1, 2, 3
    for i in [1, 2, 3]:
        (temp_proyectos / str(i)).mkdir()

    next_id = allocator.allocate_next_id()
    assert next_id == 4


def test_allocate_max_plus_one(temp_proyectos):
    """Test max + 1 rule (not first available gap)."""
    allocator = ProjectIdAllocator(temp_proyectos)

    # Create projects 1, 2, 5 (gap at 3, 4)
    for i in [1, 2, 5]:
        (temp_proyectos / str(i)).mkdir()

    next_id = allocator.allocate_next_id()
    # Should be 6 (max + 1), not 3 (first gap)
    assert next_id == 6


def test_ignore_non_numeric_dirs(temp_proyectos):
    """Test that non-numeric directories are ignored."""
    allocator = ProjectIdAllocator(temp_proyectos)

    # Create numeric and non-numeric dirs
    (temp_proyectos / "1").mkdir()
    (temp_proyectos / "2").mkdir()
    (temp_proyectos / "templates").mkdir()
    (temp_proyectos / "backup_old").mkdir()

    next_id = allocator.allocate_next_id()
    assert next_id == 3


def test_get_existing_ids(temp_proyectos):
    """Test retrieving existing project IDs."""
    allocator = ProjectIdAllocator(temp_proyectos)

    for i in [1, 3, 5, 10]:
        (temp_proyectos / str(i)).mkdir()

    existing = allocator.get_existing_ids()
    assert existing == [1, 3, 5, 10]


def test_id_exists(temp_proyectos):
    """Test checking if project ID exists."""
    allocator = ProjectIdAllocator(temp_proyectos)

    (temp_proyectos / "1").mkdir()
    (temp_proyectos / "2").mkdir()

    assert allocator.id_exists(1) is True
    assert allocator.id_exists(2) is True
    assert allocator.id_exists(3) is False


def test_ensure_project_dir(temp_proyectos):
    """Test ensuring project directory exists."""
    allocator = ProjectIdAllocator(temp_proyectos)

    # Create dir for project 1
    path = allocator.ensure_project_dir(1)
    assert path.exists()
    assert path.is_dir()
    assert path == temp_proyectos / "1"

    # Calling again should not fail
    path2 = allocator.ensure_project_dir(1)
    assert path2 == path


def test_get_project_path(temp_proyectos):
    """Test getting project path."""
    allocator = ProjectIdAllocator(temp_proyectos)
    path = allocator.get_project_path(5)
    assert path == temp_proyectos / "5"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
