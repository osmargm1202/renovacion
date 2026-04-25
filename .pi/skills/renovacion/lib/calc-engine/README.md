# Calc Engine

Air renewal calculation tooling for renovacion projects.

## Purpose
Reusable calculation engine that:
- Consumes validated `input.json` (status: `calc_ready`)
- Applies DIN 1946 air renewal rules from `rules/renovacion.json`
- Produces `resultados.json` with dual-method calculation, traces, and aggregations

## Architecture

### Modules

**rule_loader.py**
- Load rules from `renovacion.json`
- Resolve RH rules by exact match on `catalog_sector` + `catalog_type`
- Resolve people rules by `catalog_type`

**policies.py**
- Compute RH target: midpoint for ranges, direct for aprox
- Compute people target: direct for single value, midpoint for ranges
- Select governing method: `max-of-both` policy

**traces.py**
- Generate human-readable formula traces
- Generate machine-structured traces for audit

**area_engine.py**
- Calculate required m³/h per area
- Execute both RH and people methods
- Select governing result
- Emit dual traces

**aggregator.py**
- Aggregate equipment demand from served areas
- Compute project summary metrics

**runner.py**
- Main orchestrator
- Runs full calculation pipeline
- Validates input status
- Saves `resultados.json`

## Policies Implemented

### RH Method
- **Lookup**: Exact match on `catalog_sector` + `catalog_type`
- **Range resolution**: Midpoint `(min + max) / 2`
- **Aprox**: Treat as single value `min = max = aprox`
- **Formula**: `required_m3_h = volume_m3 * rh_target`
- **Error**: Missing canonical rule → calculation fails

### People Method
- **Lookup**: Match on `catalog_type` only
- **Applicability**: `people == null` → not applicable (no error)
- **Range resolution**: Midpoint (same-as-rh-policy)
- **Single value**: Use direct
- **Formula**: `required_m3_h = people * caudal_persona_target`
- **Error**: People present but no mapping → calculation fails

### Governing Method
- **Policy**: `max-of-both`
- **RH wins**: RH > people or people not applicable
- **People wins**: people > RH
- **Tie**: RH == people

### Rounding
- **Policy**: `round-2-decimals`
- All stored results rounded to 2 decimal places
- Applies to: targets, results, finals, aggregates, summary

### Tracing
- **Human trace**: Readable formula with values
  - Example: `"Q_rh = V * RH = 21.60 * 6.00 = 129.60 m3/h"`
- **Structured trace**: Machine-readable with inputs, operation, output
- Both methods always traced (even if not applicable)

## Usage

### Python API
```python
from calc_engine.runner import run_calculation
from pathlib import Path

result = run_calculation(
    input_path=Path("proyectos/1/input.json"),
    rules_path=Path("rules/renovacion.json"),
    output_path=Path("proyectos/1/resultados.json")  # optional
)

print(result['summary']['total_required_m3_h'])
```

### CLI Script
```bash
python scripts/generate_golden_example.py
```

### From calculator-agent
```python
from calc_engine import run_calculation

# calculator-agent will call this with project-specific paths
run_calculation(input_path, rules_path, output_path)
```

## Testing

Run full test suite:
```bash
cd lib/calc-engine
uv run pytest ../../tests/calc-engine/ -v
```

Test coverage:
- Rule loader: RH lookup, people lookup, not found cases
- Policies: midpoint, aprox, single values, governing selection
- Traces: human format, structured format, not applicable
- Area engine: RH only, both methods, errors, rounding
- Aggregator: single/multiple areas, summary computation
- Runner: full integration with AURORA GMR fixture

**33 tests, all passing**

## Input Requirements
- `input.json` with `status == "calc_ready"`
- All critical fields validated upstream by `input-validator-agent`
- Areas must have:
  - `catalog_type` and `catalog_sector` (from catalog normalization)
  - `dimensions.volume_m3`
  - `people` (can be `null`)
  - `equipment_ids` (can be empty)

## Output Contract
See: `docs/contracts/resultados-json.md`

Structure:
```json
{
  "project": {...},
  "summary": {...},
  "area_results": [...],
  "equipment_results": [...],
  "calculation_trace": {...}
}
```

## Error Handling

### Blocking Errors (calculation fails)
- Input status != `calc_ready`
- Missing canonical RH rule for area type
- People present but no mapping in rules
- Invalid rule format (neither min/max nor aprox/valor)

### Non-Blocking (calculation proceeds)
- `people == null` → RH method only, people marked not applicable
- Equipment with no served areas → `required_m3_h_assigned = 0.0`

## V1 Limitations
- No commercial equipment sizing (`sizing_status = "not_sized_v1"`)
- No load optimization or balancing
- Direct sum aggregation only
- Single standard (DIN 1946) only
- No multi-standard support

## Dependencies
- Python 3.13+
- No external runtime dependencies (stdlib only)
- Dev: pytest

## Next Steps for calculator-agent
1. Load project `input.json`
2. Validate status == `calc_ready`
3. Call `run_calculation(input_path, rules_path, output_path)`
4. Check result status
5. Return structured response with artifacts created
6. Handoff to spec-agent (future) or memory-agent (future)

## Golden Example
See: `proyectos/1/resultados.json` (AURORA GMR)

Expected:
- 1 area: Baño principal
- Volume: 21.6 m³
- RH: 6.0 (midpoint of 5-7)
- Result: 129.6 m³/h
- Governing: RH (people null)
- Equipment E1: 129.6 m³/h assigned

## Documentation
- Contract: `docs/contracts/resultados-json.md`
- Rules: `docs/contracts/calc-rules.md`
- Design: `docs/superpowers/specs/2026-04-22-calc-engine-design.md`
