# Input JSON Contract

## Purpose
`input.json` es artefacto base por proyecto. Guarda metadata, áreas, equipos, validación y vínculos necesarios para cálculo/spec/memoria.

Ruta:
- `.pi/skills/renovacion/proyectos/[id]/input.json`

## Top-level shape
```json
{
  "project": {},
  "validation": {},
  "areas": [],
  "equipment": [],
  "defaults_applied": []
}
```

Reglas:
- no agregar otras llaves top-level en v1
- metadata faltante se persiste como `null`, no se omite
- `equipment` se mantiene con ese nombre exacto

## `project`

| Field | Type | Required | Nullable | Notes |
|---|---|---:|---:|---|
| `id` | integer | yes | no | id secuencial local |
| `name` | string | yes | yes | nombre proyecto |
| `cliente` | string | yes | yes | cliente |
| `ubicacion` | string | yes | yes | ubicación |
| `ingeniero` | string | yes | yes | ingeniero |
| `codia` | string | yes | yes | CODIA |
| `empresa_calculo` | string | yes | yes | empresa calculista |
| `logo_empresa` | string | yes | yes | URL o referencia |
| `logo_cliente` | string | yes | yes | URL o referencia |
| `status` | enum | yes | no | `draft` o `calc_ready` |

## `validation`

| Field | Type | Required | Nullable | Notes |
|---|---|---:|---:|---|
| `critical_complete` | boolean | yes | no | derivado |
| `missing_critical` | string[] | yes | no | rutas faltantes |
| `missing_non_critical` | string[] | yes | no | rutas faltantes |
| `notes` | string[] | yes | no | validación/normalización |

## `areas[]`

| Field | Type | Required | Nullable | Notes |
|---|---|---:|---:|---|
| `id` | string | yes | no | único por proyecto |
| `alias` | string | yes | no | nombre humano |
| `catalog_type` | string | yes | no | valor canónico |
| `catalog_sector` | string | yes | no | `terciario`, `industrial`, `residencial_domestico` |
| `extractor_type` | enum | yes | no | `sencillo` o `ducteable`; uso explícito, no inferido por capacidad |
| `dimensions` | object | yes | no | ver abajo |
| `people` | integer\|number\|null | yes | yes | opcional v1 |
| `equipment_ids` | string[] | yes | no | equipos que sirven área |
| `notes` | string[] | yes | no | observaciones |

### `areas[].extractor_type`
Valores válidos:
- `sencillo`
- `ducteable`

Política:
- describe categoría de uso requerida para área
- no se infiere por CFM o m³/h
- downstream spec-engine deriva tipo de equipo desde áreas servidas

## `areas[].dimensions`
Formas válidas:

### Shape A
```json
{
  "area_m2": 8,
  "height_m": 2.7,
  "volume_m3": 21.6
}
```

### Shape B
```json
{
  "length_m": 2,
  "width_m": 4,
  "height_m": 2.7,
  "area_m2": 8,
  "volume_m3": 21.6
}
```

Reglas:
- `height_m` siempre requerido
- `volume_m3` debe existir tras normalización
- si input trae `length_m` y `width_m`, se preservan
- si input trae solo `area_m2` y `height_m`, no se inventan `length_m` ni `width_m`

## `equipment[]`

| Field | Type | Required | Nullable | Notes |
|---|---|---:|---:|---|
| `id` | string | yes | no | único por proyecto |
| `alias` | string | yes | no | nombre humano |
| `kind` | string | yes | yes | tipo funcional |
| `cantidad` | integer\|number | yes | yes | fixed-only v1 |
| `serves_area_ids` | string[] | yes | no | áreas servidas |
| `voltage` | string\|number\|null | yes | yes | placeholder |
| `frequency_hz` | number\|null | yes | yes | placeholder |
| `installation_type` | string\|null | yes | yes | placeholder |
| `power_w` | number\|null | yes | yes | placeholder |
| `power_kw` | number\|null | yes | yes | placeholder |
| `airflow_cfm` | number\|null | yes | yes | placeholder |
| `airflow_m3_h` | number\|null | yes | yes | placeholder |
| `notes` | string[] | yes | no | observaciones |

## `defaults_applied`
Lista de campos aplicados automáticamente.

## Hybrid area/equipment links
Relación explícita y consistente en dos direcciones:
- `areas[].equipment_ids`
- `equipment[].serves_area_ids`

## Example normalized payload
```json
{
  "project": {
    "id": 1,
    "name": "AURORA GMR",
    "cliente": "BOHC SRL",
    "ubicacion": "Distrito Nacional",
    "ingeniero": "Osmar Garcia",
    "codia": "36467",
    "empresa_calculo": "ORGM",
    "logo_empresa": "https://r2.or-gm.com/orgm.png",
    "logo_cliente": "https://r2.or-gm.com/bohc.png",
    "status": "calc_ready"
  },
  "validation": {
    "critical_complete": true,
    "missing_critical": [],
    "missing_non_critical": [
      "areas[0].people",
      "equipment[0].voltage",
      "equipment[0].frequency_hz",
      "equipment[0].installation_type"
    ],
    "notes": []
  },
  "areas": [
    {
      "id": "A1",
      "alias": "Baño principal",
      "catalog_type": "Cuartos de baño",
      "catalog_sector": "residencial_domestico",
      "extractor_type": "sencillo",
      "dimensions": {
        "length_m": 2,
        "width_m": 4,
        "height_m": 2.7,
        "area_m2": 8,
        "volume_m3": 21.6
      },
      "people": null,
      "equipment_ids": ["E1"],
      "notes": []
    }
  ],
  "equipment": [
    {
      "id": "E1",
      "alias": "Extractor baño principal",
      "kind": "extractor",
      "cantidad": 1,
      "serves_area_ids": ["A1"],
      "voltage": null,
      "frequency_hz": null,
      "installation_type": null,
      "power_w": null,
      "power_kw": null,
      "airflow_cfm": null,
      "airflow_m3_h": null,
      "notes": []
    }
  ],
  "defaults_applied": [
    "ingeniero",
    "codia",
    "empresa_calculo",
    "logo_empresa",
    "cliente",
    "logo_cliente",
    "ubicacion"
  ]
}
```
