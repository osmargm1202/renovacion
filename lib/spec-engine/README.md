# Spec Engine

Local-first equipment specification and selection engine for renovacion projects.

## Architecture

```
spec-engine/
├── catalog/
│   └── models.json          # Local model database
├── catalog_loader.py        # Load catalog JSON
├── catalog_validator.py     # Validate model entries
├── filters.py               # Apply eligibility filters
├── selector.py              # Select best model (closest-airflow-above + lower-power)
├── assembler.py             # Assemble spec.json structure
└── runner.py                # Orchestrate full pipeline
```

## Contracts

- **spec.json contract**: `docs/contracts/spec-json.md`
- **Local catalog contract**: `docs/contracts/local-catalog.md`

## Policies

### Selection Strategy
- **Source**: `local-only` (no web fallback)
- **Mode**: `auto-select-model`
- **Basis**: `hybrid` (identity from input.json, demand from resultados.json)

### Selection Criterion
- **Primary**: `closest-airflow-above` (minimum excess over required)
- **Tie-break**: `lower-power` (minimum power_w)

### Failure Rule
- No model below required airflow
- No multi-unit optimization
- No web fallback
- Status: `failed` with `selected_model = null`

### Alternatives
- Top 3 valid models excluding selected
- Ordered by selection criterion
- Empty if < 2 total valid models

## Usage

### Python Runner

```python
from pathlib import Path
from lib.spec_engine.runner import run_spec_generation

project_path = Path('proyectos/1')
catalog_path = Path('lib/spec-engine/catalog/models.json')

spec = run_spec_generation(project_path, catalog_path)

# Save output
import json
output_path = project_path / 'spec.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(spec, f, indent=2, ensure_ascii=False)
```

### Module-by-Module

```python
import json
from pathlib import Path
from lib.spec_engine import (
    catalog_loader,
    catalog_validator,
    filters,
    selector,
    assembler
)

# Load catalog
catalog_path = Path('lib/spec-engine/catalog/models.json')
catalog_data = catalog_loader.load_catalog(catalog_path)
models = catalog_loader.get_models(catalog_data)

# Validate
is_valid, invalid = catalog_validator.validate_catalog(models)
if not is_valid:
    raise ValueError(f"Invalid catalog: {invalid}")

# Filter models
filtered = filters.apply_filters(
    models,
    kind='extractor',
    installation_type='muro',
    voltage=120,
    frequency_hz=60
)

# Get eligible models
eligible = filters.get_eligible_models(filtered, required_m3_h=129.6)

# Select best model
selected, reason = selector.select_model(eligible, required_m3_h=129.6)

# Get alternatives
alternatives = selector.get_alternatives(eligible, selected, required_m3_h=129.6)

# Format output
formatted_model = assembler.format_model(selected)
```

## Testing

Tests located in `tests/spec-engine/`:
- `test_catalog_validator.py` - catalog validation
- `test_filters.py` - eligibility filters
- `test_selector.py` - selection and alternatives
- `test_assembler.py` - spec assembly
- `test_runner.py` - full pipeline integration

Run with pytest:
```bash
python -m pytest tests/spec-engine/ -v
```

## Golden Example

Input:
- `proyectos/1/input.json` (AURORA GMR)
- `proyectos/1/resultados.json`
- `lib/spec-engine/catalog/models.json`

Output:
- `proyectos/1/spec.json`

Equipment E1 requires 129.6 m³/h:
- Selected: EX-150 (140.0 m³/h, 45W)
- Alternatives: EX-160, EX-200, EX-250

## Catalog Management

### Adding Models

Edit `lib/spec-engine/catalog/models.json`:

```json
{
  "brand": "ORGM",
  "model": "EX-300",
  "kind": "extractor",
  "airflow_m3_h": 300.0,
  "voltage": 120,
  "frequency_hz": 60,
  "power_w": 90,
  "power_kw": 0.09,
  "installation_type": "muro",
  "image_asset": "assets/extractores/ex-300.png",
  "notes": []
}
```

### Required Fields
- `brand`, `model`, `kind`
- `airflow_m3_h` (> 0)
- `voltage` (> 0)
- `frequency_hz` (> 0)
- `power_w`, `power_kw` (>= 0, consistent)
- `installation_type`

### Validation
Catalog validated on load. Invalid models cause pipeline failure.

## Version
v1 - 2026-04-23
