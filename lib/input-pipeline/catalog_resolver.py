#!/usr/bin/env python3
"""
Catalog resolver using normalized+synonyms policy against rules/renovacion.json.
No fuzzy matching. Explicit normalization + synonym mapping only.
"""

import json
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def normalize_text(text: str) -> str:
    """
    Normalize text for catalog matching:
    - strip whitespace
    - lowercase
    - collapse multiple spaces
    - remove accents
    """
    # Remove accents
    normalized = "".join(
        c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn"
    )
    # Lowercase, strip, collapse spaces
    normalized = " ".join(normalized.lower().strip().split())
    return normalized


class CatalogResolver:
    """Resolves area types to canonical catalog_type + catalog_sector."""

    def __init__(self, catalog_path: str = None):
        if catalog_path is None:
            catalog_path = Path(__file__).parent.parent.parent / "rules" / "renovacion.json"
        with open(catalog_path, encoding="utf-8") as f:
            self.catalog = json.load(f)

        # Build normalized lookup
        self.canonical_map = {}  # normalized → (canonical_type, sector)
        self.synonym_map = self._build_synonym_map()

        for table in self.catalog.get("tablas_renovaciones_aire", []):
            sector = table["sector"]
            for local in table["locales"]:
                tipo = local["tipo_de_local"]
                norm = normalize_text(tipo)
                self.canonical_map[norm] = (tipo, sector)

    def _build_synonym_map(self) -> Dict[str, str]:
        """
        Build explicit synonym map.
        This is extensible - add more synonyms as needed.
        Returns: {normalized_synonym → normalized_canonical}
        """
        # Explicit synonyms for common variations
        synonyms = {
            "baño": "cuartos de baño",
            "baños": "cuartos de baño",
            "wc": "cuartos de baño",
            "sanitario": "cuartos de baño",
            "sanitarios": "cuartos de baño",
            "cocina": "cocinas residenciales",
            "cocina domestica": "cocinas residenciales",
            "cocina casera": "cocinas residenciales",
            "habitacion": "habitaciones residenciales",
            "cuarto": "habitaciones residenciales",
            "dormitorio": "habitaciones residenciales",
            "recamara": "habitaciones residenciales",
            "oficina": "oficinas",
            "despacho": "despachos de reuniones",
            "sala de juntas": "salas de reuniones",
            "almacen": "almacenes",
            "bodega": "almacenes",
            "garage": "garages",
            "estacionamiento": "garages",
            "parqueo": "garages",
        }

        # Normalize both keys and values
        return {normalize_text(k): normalize_text(v) for k, v in synonyms.items()}

    def resolve(self, raw_type: str) -> Tuple[Optional[str], Optional[str], List[str]]:
        """
        Resolve raw input to (catalog_type, catalog_sector, notes).

        Resolution order:
        1. Exact canonical match (normalized)
        2. Synonym match
        3. None (unresolved)

        Returns:
            (catalog_type, catalog_sector, notes) where:
            - catalog_type is canonical from rules/renovacion.json
            - catalog_sector is one of: terciario, industrial, residencial_domestico
            - notes is list of resolution messages
        """
        notes = []
        normalized = normalize_text(raw_type)

        # 1. Exact canonical match
        if normalized in self.canonical_map:
            canonical_type, sector = self.canonical_map[normalized]
            if normalized != normalize_text(canonical_type):
                notes.append(f"Normalized '{raw_type}' to canonical '{canonical_type}'")
            return canonical_type, sector, notes

        # 2. Synonym match
        if normalized in self.synonym_map:
            canonical_norm = self.synonym_map[normalized]
            if canonical_norm in self.canonical_map:
                canonical_type, sector = self.canonical_map[canonical_norm]
                notes.append(f"Resolved synonym '{raw_type}' → '{canonical_type}'")
                return canonical_type, sector, notes

        # 3. Unresolved
        notes.append(f"Could not resolve '{raw_type}' to catalog")
        return None, None, notes

    def get_sector_types(self, sector: str) -> List[str]:
        """Get all canonical types for a given sector."""
        types = []
        for table in self.catalog.get("tablas_renovaciones_aire", []):
            if table["sector"] == sector:
                types.extend([local["tipo_de_local"] for local in table["locales"]])
        return types

    def get_all_types(self) -> List[str]:
        """Get all canonical types across all sectors."""
        types = []
        for table in self.catalog.get("tablas_renovaciones_aire", []):
            types.extend([local["tipo_de_local"] for local in table["locales"]])
        return types

    def get_renovations_range(self, catalog_type: str, sector: str = None) -> Optional[Dict]:
        """
        Get renovations per hour range for a given catalog type.
        Returns: {min, max, aprox, tipo} or None if not found
        """
        for table in self.catalog.get("tablas_renovaciones_aire", []):
            if sector and table["sector"] != sector:
                continue
            for local in table["locales"]:
                if local["tipo_de_local"] == catalog_type:
                    return local.get("renovaciones_aire_por_hora")
        return None


def main():
    """CLI entry point for testing catalog resolution."""
    import sys

    resolver = CatalogResolver()

    if len(sys.argv) < 2:
        print("Usage: catalog_resolver.py <type_to_resolve>")
        print("\nAvailable canonical types:")
        for tipo in sorted(resolver.get_all_types()):
            print(f"  - {tipo}")
        sys.exit(1)

    raw_input = " ".join(sys.argv[1:])
    catalog_type, sector, notes = resolver.resolve(raw_input)

    print("=" * 60)
    print(f"Input: {raw_input}")
    print("=" * 60)

    if catalog_type:
        print(f"✓ Resolved")
        print(f"  Catalog Type: {catalog_type}")
        print(f"  Sector: {sector}")

        reno_range = resolver.get_renovations_range(catalog_type, sector)
        if reno_range:
            print(f"  Renovations/hour: {reno_range}")
    else:
        print("✗ Could not resolve")

    if notes:
        print("\nNotes:")
        for note in notes:
            print(f"  - {note}")


if __name__ == "__main__":
    main()
