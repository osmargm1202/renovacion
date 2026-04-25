#!/usr/bin/env python3
"""
Project ID allocator using sequential integer policy.
Scans /proyectos/ for existing numeric directories, returns max + 1.
"""

from pathlib import Path
from typing import Optional


class ProjectIdAllocator:
    """Allocates sequential project IDs based on existing /proyectos/ structure."""

    def __init__(self, base_path: str = None):
        if base_path is None:
            # Default: assume we're in repo root or use relative path
            base_path = Path(__file__).parent.parent.parent / "proyectos"
        self.base_path = Path(base_path)

    def get_existing_ids(self) -> list[int]:
        """Scan /proyectos/ and return list of existing numeric project IDs."""
        if not self.base_path.exists():
            return []

        ids = []
        for item in self.base_path.iterdir():
            if item.is_dir() and item.name.isdigit():
                ids.append(int(item.name))
        return sorted(ids)

    def allocate_next_id(self) -> int:
        """
        Allocate next sequential project ID.
        Rule: max + 1 (or 1 if no projects exist).
        """
        existing = self.get_existing_ids()
        if not existing:
            return 1
        return max(existing) + 1

    def id_exists(self, project_id: int) -> bool:
        """Check if a specific project ID already exists."""
        project_dir = self.base_path / str(project_id)
        return project_dir.exists() and project_dir.is_dir()

    def get_project_path(self, project_id: int) -> Path:
        """Get path for a given project ID."""
        return self.base_path / str(project_id)

    def ensure_project_dir(self, project_id: int) -> Path:
        """Ensure project directory exists, create if necessary. Returns path."""
        project_path = self.get_project_path(project_id)
        project_path.mkdir(parents=True, exist_ok=True)
        return project_path

    def find_by_name(self, name: str, case_sensitive: bool = False) -> Optional[int]:
        """
        Find existing project by name (reads input.json from each project).
        Returns project_id if exact match found, None otherwise.
        Warning: This scans all projects and is slow for many projects.
        """
        import json

        existing_ids = self.get_existing_ids()
        for pid in existing_ids:
            input_path = self.get_project_path(pid) / "input.json"
            if not input_path.exists():
                continue
            try:
                with open(input_path) as f:
                    data = json.load(f)
                    project_name = data.get("project", {}).get("name")
                    if project_name:
                        if case_sensitive:
                            if project_name == name:
                                return pid
                        else:
                            if project_name.lower() == name.lower():
                                return pid
            except (json.JSONDecodeError, OSError):
                continue
        return None


def main():
    """CLI entry point for testing."""
    import sys

    allocator = ProjectIdAllocator()

    if "--next" in sys.argv:
        next_id = allocator.allocate_next_id()
        print(f"Next project ID: {next_id}")
        print(f"Path: {allocator.get_project_path(next_id)}")

    elif "--list" in sys.argv:
        existing = allocator.get_existing_ids()
        if existing:
            print(f"Existing project IDs: {existing}")
            print(f"Next available: {max(existing) + 1}")
        else:
            print("No existing projects. Next ID: 1")

    elif "--find" in sys.argv and len(sys.argv) > 2:
        name = " ".join(sys.argv[2:])
        found = allocator.find_by_name(name)
        if found:
            print(f"Found project '{name}' with ID: {found}")
        else:
            print(f"No project found with name: {name}")

    else:
        print("Usage:")
        print("  project_id_allocator.py --next         # Get next available ID")
        print("  project_id_allocator.py --list         # List existing IDs")
        print("  project_id_allocator.py --find <name>  # Find project by name")


if __name__ == "__main__":
    main()
