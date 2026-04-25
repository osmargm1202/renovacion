#!/usr/bin/env python3
"""Tests for catalog resolution with normalized+synonyms policy."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib" / "input-pipeline"))

from catalog_resolver import CatalogResolver, normalize_text


@pytest.fixture
def resolver():
    return CatalogResolver()


def test_normalize_text():
    """Test text normalization: trim, lowercase, collapse spaces, remove accents."""
    assert normalize_text("  Cuartos de Baño  ") == "cuartos de bano"
    assert normalize_text("HABITACIONES") == "habitaciones"
    assert normalize_text("Salas  de   Reuniones") == "salas de reuniones"
    assert normalize_text("Café") == "cafe"
    assert normalize_text("Niño") == "nino"


def test_resolve_exact_canonical(resolver):
    """Test exact canonical match (normalized)."""
    catalog_type, sector, notes = resolver.resolve("Cuartos de baño")
    assert catalog_type == "Cuartos de baño"
    assert sector == "residencial_domestico"

    # Case insensitive + trimmed
    catalog_type, sector, notes = resolver.resolve("  CUARTOS DE BAÑO  ")
    assert catalog_type == "Cuartos de baño"
    assert sector == "residencial_domestico"


def test_resolve_synonym(resolver):
    """Test synonym resolution."""
    # "baño" → "Cuartos de baño"
    catalog_type, sector, notes = resolver.resolve("baño")
    assert catalog_type == "Cuartos de baño"
    assert sector == "residencial_domestico"
    assert any("synonym" in n.lower() for n in notes)

    # "oficina" → "Oficinas"
    catalog_type, sector, notes = resolver.resolve("oficina")
    assert catalog_type == "Oficinas"
    assert sector == "terciario"


def test_resolve_unresolved(resolver):
    """Test unresolved input returns None."""
    catalog_type, sector, notes = resolver.resolve("tipo_inventado_xyz")
    assert catalog_type is None
    assert sector is None
    assert any("could not resolve" in n.lower() for n in notes)


def test_get_sector_types(resolver):
    """Test retrieving all types for a sector."""
    residencial = resolver.get_sector_types("residencial_domestico")
    assert "Cuartos de baño" in residencial
    assert "Cocinas residenciales" in residencial

    terciario = resolver.get_sector_types("terciario")
    assert "Oficinas" in terciario
    assert "Restaurantes" in terciario

    industrial = resolver.get_sector_types("industrial")
    assert "Almacenes" in industrial
    assert "Laboratorios" in industrial


def test_get_all_types(resolver):
    """Test retrieving all canonical types."""
    all_types = resolver.get_all_types()
    assert "Cuartos de baño" in all_types
    assert "Oficinas" in all_types
    assert "Almacenes" in all_types
    assert len(all_types) > 30  # Should have many types across sectors


def test_get_renovations_range(resolver):
    """Test retrieving renovations per hour range."""
    reno = resolver.get_renovations_range("Cuartos de baño", "residencial_domestico")
    assert reno is not None
    assert "min" in reno
    assert "max" in reno
    assert reno["min"] == 5
    assert reno["max"] == 7

    reno = resolver.get_renovations_range("Oficinas", "terciario")
    assert reno is not None
    assert reno["min"] == 4
    assert reno["max"] == 8


def test_resolve_accent_variations(resolver):
    """Test accent variations resolve correctly."""
    # With accent
    catalog_type, sector, notes = resolver.resolve("Cuartos de baño")
    assert catalog_type == "Cuartos de baño"

    # Without accent (normalized)
    catalog_type, sector, notes = resolver.resolve("Cuartos de bano")
    assert catalog_type == "Cuartos de baño"


def test_resolve_multiple_synonyms(resolver):
    """Test multiple synonyms for same canonical type."""
    for synonym in ["baño", "baños", "wc", "sanitario"]:
        catalog_type, sector, notes = resolver.resolve(synonym)
        assert catalog_type == "Cuartos de baño"
        assert sector == "residencial_domestico"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
