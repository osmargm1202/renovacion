# Renovacion

Self-contained Pi skill for renovation-airflow calculation, equipment specification, and HTML memory generation.

## Source of truth

Runtime code and project artifacts live under `.pi/skills/renovacion/`.

Project artifacts are stored under `.pi/skills/renovacion/proyectos/[id]/`.

## Validate

```bash
python .pi/skills/renovacion/scripts/validate-skill-structure.py
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
bash .pi/skills/renovacion/scripts/run-project.sh 1
```

## Notes

The commercial extractor catalog is local JSON. Runtime does not perform live web lookup for equipment models or equipment images.
