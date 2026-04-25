import importlib
import importlib.util
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SPEC_ENGINE_ROOT = SKILL_ROOT / "lib" / "spec-engine"
CATALOG_PATH = SPEC_ENGINE_ROOT / "catalog" / "models.json"
PACKAGE_NAME = "renovacion_spec_engine"


def load_spec_engine_module(module_name: str):
    spec = importlib.util.spec_from_file_location(
        PACKAGE_NAME,
        SPEC_ENGINE_ROOT / "__init__.py",
        submodule_search_locations=[str(SPEC_ENGINE_ROOT)],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec engine package from {SPEC_ENGINE_ROOT}")
    package = importlib.util.module_from_spec(spec)
    sys.modules[PACKAGE_NAME] = package
    spec.loader.exec_module(package)
    return importlib.import_module(f"{PACKAGE_NAME}.{module_name}")


def load_catalog_models():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))["models"]


def write_project_files(project_path: Path, *, area_types: list[str], required_m3_h: float):
    area_ids = [f"A{index + 1}" for index in range(len(area_types))]
    input_data = {
        "project": {"id": 99, "name": "Extractor Type Test"},
        "areas": [
            {
                "id": area_id,
                "alias": f"Area {index + 1}",
                "extractor_type": extractor_type,
                "equipment_ids": ["E1"],
            }
            for index, (area_id, extractor_type) in enumerate(zip(area_ids, area_types))
        ],
        "equipment": [
            {
                "id": "E1",
                "alias": "Equipo principal",
                "kind": "extractor",
                "serves_area_ids": area_ids,
                "installation_type": None,
                "voltage": None,
                "frequency_hz": None,
            }
        ],
    }
    results_data = {
        "equipment_results": [
            {
                "equipment_id": "E1",
                "required_m3_h_assigned": required_m3_h,
            }
        ]
    }
    (project_path / "input.json").write_text(json.dumps(input_data), encoding="utf-8")
    (project_path / "resultados.json").write_text(json.dumps(results_data), encoding="utf-8")



def test_apply_filters_with_extractor_type_returns_only_matching_models():
    filters = load_spec_engine_module("filters")
    models = load_catalog_models()

    filtered = filters.apply_filters(models, kind="extractor", extractor_type="ducteable")

    assert filtered
    assert {model["extractor_type"] for model in filtered} == {"ducteable"}



def test_ducteable_equipment_never_selects_closer_simple_model(tmp_path):
    runner = load_spec_engine_module("runner")
    project_path = tmp_path / "project"
    project_path.mkdir()
    write_project_files(project_path, area_types=["ducteable"], required_m3_h=150.0)

    spec = runner.run_spec_generation(project_path, CATALOG_PATH)

    selected = spec["equipment_specs"][0]["selected_model"]
    assert selected["extractor_type"] == "ducteable"
    assert selected["model"] == "TD-MIXVENT 100"



def test_mixed_served_area_types_resolve_to_ducteable():
    runner = load_spec_engine_module("runner")
    input_data = {
        "areas": [
            {"id": "A1", "extractor_type": "sencillo"},
            {"id": "A2", "extractor_type": "ducteable"},
        ]
    }
    equipment = {"serves_area_ids": ["A1", "A2"]}

    extractor_type = runner.derive_equipment_extractor_type(equipment, input_data)

    assert extractor_type == "ducteable"



def test_selected_model_output_includes_source_and_provenance_fields(tmp_path):
    runner = load_spec_engine_module("runner")
    project_path = tmp_path / "project"
    project_path.mkdir()
    write_project_files(project_path, area_types=["ducteable"], required_m3_h=150.0)

    spec = runner.run_spec_generation(project_path, CATALOG_PATH)

    equipment_spec = spec["equipment_specs"][0]
    selected = equipment_spec["selected_model"]
    alternative = equipment_spec["alternatives"][0]

    assert equipment_spec["extractor_type"] == "ducteable"
    assert equipment_spec["constraints_used"]["extractor_type"] == "ducteable"
    for model in [selected, alternative]:
        for field in [
            "extractor_type",
            "airflow_cfm",
            "source_url",
            "catalog_url",
            "image_source_url",
            "rating_basis",
            "source_notes",
            "retrieved_at",
        ]:
            assert field in model
