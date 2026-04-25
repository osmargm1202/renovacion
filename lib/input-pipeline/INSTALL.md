# Installation

## Dependencies

Install required Python packages:

```bash
pip install jsonschema pytest
```

Or from requirements file:

```bash
pip install -r requirements.txt
```

## Verification

Test each component:

### 1. Catalog Resolver (no dependencies)
```bash
python3 catalog_resolver.py "baño"
```

Expected output:
```
✓ Resolved
  Catalog Type: Cuartos de baño
  Sector: residencial_domestico
  Renovations/hour: {'min': 5, 'max': 7}
```

### 2. Project ID Allocator (no dependencies)
```bash
python3 project_id_allocator.py --list
```

Expected output:
```
No existing projects. Next ID: 1
```

### 3. Validator (requires jsonschema)
```bash
python3 validator.py ../../examples/input-pipeline/aurora-gmr.input.json
```

Expected output:
```
VALIDATION RESULT
Valid: True
Critical Complete: True
```

### 4. Run Tests (requires pytest + jsonschema)
```bash
cd ../../tests/input-pipeline
pytest -v
```

## Docker Alternative

If dependencies conflict with system Python:

```bash
docker run -it --rm -v $(pwd):/work -w /work python:3.11 bash
pip install jsonschema pytest
python3 validator.py examples/input-pipeline/aurora-gmr.input.json
```
