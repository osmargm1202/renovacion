# Local Catalog Contract

## Purpose
Catálogo local source-backed para selección comercial de extractores. Runtime es `local-only`; no hace lookup web en ejecución.

## Location
`.pi/skills/renovacion/lib/spec-engine/catalog/models.json`

## Top-level structure
```json
{
  "catalog": {
    "version": "2",
    "source": "commercial-catalog-v2",
    "last_updated": "2026-04-25"
  },
  "models": []
}
```

## Required model fields
Cada entrada debe incluir:
- `brand`
- `model`
- `kind`
- `extractor_type`
- `airflow_cfm`
- `airflow_m3_h`
- `airflow_unit_original`
- `voltage`
- `frequency_hz`
- `power_w`
- `power_kw`
- `power_unit_original`
- `installation_type`
- `image_asset`
- `source_url`
- `catalog_url`
- `image_source_url`
- `rating_basis`
- `source_notes`
- `retrieved_at`
- `notes`

Opcional:
- `power_hp`

## Validation rules
- `extractor_type ∈ {sencillo, ducteable}`
- `airflow_cfm > 0`
- `airflow_m3_h > 0`
- `voltage` acepta número positivo o string no vacío
- `frequency_hz` acepta número positivo o string no vacío
- `power_w >= 0`
- `power_kw >= 0`
- `power_kw == power_w / 1000`
- strings requeridos no pueden ir vacíos

## Image policy
Runtime usa solo dos imágenes locales por categoría:
- `assets/extractores/sencillo.png`
- `assets/extractores/ducteable.png`

Reglas:
- `image_asset` debe ser una de esas dos rutas
- no URLs remotas en `image_asset`
- `image_source_url` existe solo como procedencia, no para descarga runtime

## Source/provenance policy
Catálogo conserva procedencia por modelo:
- `source_url`: página fuente principal
- `catalog_url`: PDF o ficha técnica
- `image_source_url`: URL fuente de imagen original
- `rating_basis`: base de rating (`HVI 0.1 in wg`, `Manufacturer maximum airflow`, etc.)
- `source_notes`: nota corta audit trail
- `retrieved_at`: fecha de captura
- `airflow_unit_original`: unidad original reportada por fuente (`CFM`, `m3/h`, etc.)
- `power_unit_original`: unidad original reportada por fuente (`W`, `kW`, etc.)
- `notes`: lista de notas internas/additivas por fila

## Selection compatibility
Modelos se filtran por:
- `kind` exacto
- `extractor_type` exacto
- `installation_type` exacto si input lo especifica
- `voltage` exacto si input lo especifica
- `frequency_hz` exacto si input lo especifica

Elegibilidad:
- modelo pasa filtros
- `airflow_m3_h >= required_m3_h`

## Seed data policy
- usar modelos comerciales source-backed
- no incluir entradas sintéticas `EX-*` ni `INY-*`
- categorías simples usan `extractor_type: sencillo`
- categorías ductables usan `extractor_type: ducteable`
- semillas Sodeca aprobadas incluyen familias `NEOLINEO`, `NEOSILENT`, `CA/LINE`, `TUB`
