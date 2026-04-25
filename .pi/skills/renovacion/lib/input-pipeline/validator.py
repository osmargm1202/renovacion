#!/usr/bin/env python3
"""
Input.json validator with critical/non-critical field handling,
dimensions normalization, cross-link validation, and draft/calc_ready status.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import jsonschema


CRITICAL_FIELDS = {
    "project": ["id", "name", "ubicacion"],
    "area": ["id", "alias", "catalog_type", "extractor_type", "dimensions"],
}


class InputValidator:
    """Validates input.json against contract and business rules."""

    def __init__(self, schema_path: str = None):
        if schema_path is None:
            schema_path = Path(__file__).parent / "schema.json"
        with open(schema_path) as f:
            self.schema = json.load(f)

    def validate_schema(self, data: Dict[str, Any]) -> List[str]:
        """Validate against JSON schema. Returns list of errors."""
        errors = []
        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema validation: {e.message} at {'.'.join(str(p) for p in e.path)}")
        except jsonschema.SchemaError as e:
            errors.append(f"Invalid schema: {e.message}")
        return errors

    def validate_critical_fields(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check critical fields. Returns (complete, missing_paths).
        Critical:
        - project.id, project.name, project.ubicacion
        - at least one area
        - per area: id, alias, catalog_type, extractor_type, dimensions sufficient for volume
        """
        missing = []

        # Project critical fields
        project = data.get("project", {})
        for field in CRITICAL_FIELDS["project"]:
            val = project.get(field)
            if val is None or (isinstance(val, str) and not val.strip()):
                missing.append(f"project.{field}")

        # At least one area required
        areas = data.get("areas", [])
        if not areas:
            missing.append("areas")
            return False, missing

        # Per-area critical fields
        for idx, area in enumerate(areas):
            for field in CRITICAL_FIELDS["area"]:
                if field == "dimensions":
                    dims = area.get("dimensions", {})
                    height = dims.get("height_m")
                    if height is None or height <= 0:
                        missing.append(f"areas[{idx}].dimensions.height_m")
                    # Must have either area_m2 or (length_m + width_m) to derive volume
                    has_area = dims.get("area_m2") is not None and dims.get("area_m2") > 0
                    has_length_width = (
                        dims.get("length_m") is not None
                        and dims.get("width_m") is not None
                        and dims.get("length_m") > 0
                        and dims.get("width_m") > 0
                    )
                    if not has_area and not has_length_width:
                        missing.append(f"areas[{idx}].dimensions (need area_m2 or length_m+width_m)")
                else:
                    val = area.get(field)
                    if val is None or (isinstance(val, str) and not val.strip()):
                        missing.append(f"areas[{idx}].{field}")

        complete = len(missing) == 0
        return complete, missing

    def validate_non_critical_fields(self, data: Dict[str, Any]) -> List[str]:
        """
        Check non-critical fields (metadata and placeholders).
        Returns list of paths for missing non-critical fields.
        """
        missing = []
        project = data.get("project", {})

        # Non-critical project metadata
        for field in ["cliente", "ingeniero", "codia", "empresa_calculo", "logo_empresa", "logo_cliente"]:
            if project.get(field) is None:
                missing.append(f"project.{field}")

        # Non-critical area fields
        for idx, area in enumerate(data.get("areas", [])):
            if area.get("people") is None:
                missing.append(f"areas[{idx}].people")

        # Non-critical equipment placeholders
        for idx, equip in enumerate(data.get("equipment", [])):
            placeholders = [
                "voltage",
                "frequency_hz",
                "installation_type",
                "power_w",
                "power_kw",
                "airflow_cfm",
                "airflow_m3_h",
            ]
            for field in placeholders:
                if equip.get(field) is None:
                    missing.append(f"equipment[{idx}].{field}")

        return missing

    def normalize_dimensions(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Normalize area dimensions. Returns (normalized_data, notes).
        Rules:
        - If length_m + width_m provided: derive area_m2, preserve length/width
        - If area_m2 provided: use directly
        - Always derive volume_m3 = area_m2 * height_m
        """
        notes = []
        normalized = json.loads(json.dumps(data))  # deep copy

        for idx, area in enumerate(normalized.get("areas", [])):
            dims = area.get("dimensions", {})
            length = dims.get("length_m")
            width = dims.get("width_m")
            area_m2 = dims.get("area_m2")
            height = dims.get("height_m")

            if length is not None and width is not None:
                # Shape B: derive area from length * width
                derived_area = round(length * width, 2)
                if area_m2 is None:
                    dims["area_m2"] = derived_area
                    notes.append(f"areas[{idx}].dimensions.area_m2 derived from length_m * width_m")
                elif abs(area_m2 - derived_area) > 0.01:
                    # Conflict: provided area doesn't match length*width
                    notes.append(
                        f"areas[{idx}].dimensions.area_m2 mismatch: provided {area_m2}, "
                        f"derived {derived_area} from length*width. Using derived."
                    )
                    dims["area_m2"] = derived_area
                area_m2 = dims["area_m2"]

            if area_m2 is not None and height is not None:
                # Derive volume
                dims["volume_m3"] = round(area_m2 * height, 2)
                if "volume_m3" not in area.get("dimensions", {}):
                    notes.append(f"areas[{idx}].dimensions.volume_m3 derived from area_m2 * height_m")

        return normalized, notes

    def validate_cross_links(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate area ↔ equipment cross-references.
        Rules:
        - If area references equipment E, E must reference that area
        - If equipment references area A, A must reference that equipment
        - No dangling references
        """
        errors = []
        areas = {a["id"]: a for a in data.get("areas", [])}
        equipment = {e["id"]: e for e in data.get("equipment", [])}

        # Check area → equipment links
        for area in data.get("areas", []):
            for eq_id in area.get("equipment_ids", []):
                if eq_id not in equipment:
                    errors.append(f"Area {area['id']} references non-existent equipment {eq_id}")
                elif area["id"] not in equipment[eq_id].get("serves_area_ids", []):
                    errors.append(
                        f"Area {area['id']} references equipment {eq_id}, "
                        f"but {eq_id} does not reference area {area['id']}"
                    )

        # Check equipment → area links
        for equip in data.get("equipment", []):
            for area_id in equip.get("serves_area_ids", []):
                if area_id not in areas:
                    errors.append(f"Equipment {equip['id']} references non-existent area {area_id}")
                elif equip["id"] not in areas[area_id].get("equipment_ids", []):
                    errors.append(
                        f"Equipment {equip['id']} references area {area_id}, "
                        f"but {area_id} does not reference equipment {equip['id']}"
                    )

        return errors

    def validate_unique_ids(self, data: Dict[str, Any]) -> List[str]:
        """Check for duplicate area or equipment IDs."""
        errors = []

        area_ids = [a["id"] for a in data.get("areas", [])]
        if len(area_ids) != len(set(area_ids)):
            duplicates = [aid for aid in area_ids if area_ids.count(aid) > 1]
            errors.append(f"Duplicate area IDs: {set(duplicates)}")

        equip_ids = [e["id"] for e in data.get("equipment", [])]
        if len(equip_ids) != len(set(equip_ids)):
            duplicates = [eid for eid in equip_ids if equip_ids.count(eid) > 1]
            errors.append(f"Duplicate equipment IDs: {set(duplicates)}")

        return errors

    def validate(self, data: Dict[str, Any], normalize: bool = True) -> Dict[str, Any]:
        """
        Full validation pipeline. Returns validation result dict.
        If normalize=True, also normalizes dimensions.

        Returns:
        {
            "valid": bool,
            "errors": List[str],
            "critical_complete": bool,
            "missing_critical": List[str],
            "missing_non_critical": List[str],
            "notes": List[str],
            "normalized_data": Dict (if normalize=True and valid)
        }
        """
        result = {
            "valid": False,
            "errors": [],
            "critical_complete": False,
            "missing_critical": [],
            "missing_non_critical": [],
            "notes": [],
        }

        # Schema validation
        schema_errors = self.validate_schema(data)
        if schema_errors:
            result["errors"].extend(schema_errors)
            return result

        # Unique IDs
        id_errors = self.validate_unique_ids(data)
        if id_errors:
            result["errors"].extend(id_errors)
            return result

        # Cross-link validation
        link_errors = self.validate_cross_links(data)
        if link_errors:
            result["errors"].extend(link_errors)
            return result

        # Normalize dimensions
        normalized_data = data
        if normalize:
            normalized_data, norm_notes = self.normalize_dimensions(data)
            result["notes"].extend(norm_notes)

        # Critical fields
        critical_complete, missing_critical = self.validate_critical_fields(normalized_data)
        result["critical_complete"] = critical_complete
        result["missing_critical"] = missing_critical

        # Non-critical fields
        result["missing_non_critical"] = self.validate_non_critical_fields(normalized_data)

        # Valid if no hard errors
        result["valid"] = len(result["errors"]) == 0

        if normalize and result["valid"]:
            result["normalized_data"] = normalized_data

        return result


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: validator.py <input.json>")
        sys.exit(1)

    validator = InputValidator()
    with open(sys.argv[1]) as f:
        data = json.load(f)

    result = validator.validate(data, normalize=True)

    print("=" * 60)
    print("VALIDATION RESULT")
    print("=" * 60)
    print(f"Valid: {result['valid']}")
    print(f"Critical Complete: {result['critical_complete']}")
    print()

    if result["errors"]:
        print("ERRORS:")
        for err in result["errors"]:
            print(f"  - {err}")
        print()

    if result["missing_critical"]:
        print("MISSING CRITICAL:")
        for field in result["missing_critical"]:
            print(f"  - {field}")
        print()

    if result["missing_non_critical"]:
        print("MISSING NON-CRITICAL:")
        for field in result["missing_non_critical"]:
            print(f"  - {field}")
        print()

    if result["notes"]:
        print("NOTES:")
        for note in result["notes"]:
            print(f"  - {note}")
        print()

    if "normalized_data" in result:
        print("Normalized data available.")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
