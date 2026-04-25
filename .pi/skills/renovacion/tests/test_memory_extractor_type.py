import json
import subprocess
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SECTION_PATH = SKILL_ROOT / "lib" / "memory-engine" / "sections" / "seleccion-equipos.js"


def test_render_seleccion_equipos_includes_extractor_type_and_selected_model_text():
    spec_data = {
        "equipment_specs": [
            {
                "equipment_id": "E1",
                "equipment_alias": "Extractor cocina",
                "kind": "extractor",
                "required_m3_h": 344.9,
                "selection_status": "selected",
                "selection_reason": "Selected ductable model.",
                "selected_model": {
                    "brand": "S&P USA",
                    "model": "TD-SILENT 125XS",
                    "extractor_type": "ducteable",
                    "airflow_m3_h": 344.9,
                    "voltage": 120,
                    "frequency_hz": 60,
                    "power_w": 36.0,
                    "power_kw": 0.036,
                    "installation_type": "inline_circular_duct",
                },
                "alternatives": [],
            }
        ]
    }
    staged_assets = {"equipment": []}
    script = f"""
const {{ renderSeleccionEquipos }} = require({json.dumps(str(SECTION_PATH))});
const specData = {json.dumps(spec_data)};
const stagedAssets = {json.dumps(staged_assets)};
const html = renderSeleccionEquipos(specData, stagedAssets);
process.stdout.write(html);
"""

    result = subprocess.run(["node", "-e", script], text=True, capture_output=True, check=True)

    html = result.stdout
    assert "Tipo de extractor: ducteable" in html
    assert "TD-SILENT 125XS" in html
