# Input JSON Contract

## Purpose
`input.json` es artefacto base de cada proyecto de renovación. Guarda metadata de proyecto, áreas normalizadas, equipos, vínculos explícitos entre áreas y equipos, y estado de validación para permitir cálculo posterior.

Ruta objetivo:
- `/proyectos/[id]/input.json`

## Top-Level Shape
Primera versión usa exactamente estas llaves:

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
- campos faltantes de metadata se guardan como `null`, no se omiten
- `equipment` se mantiene con ese nombre exacto

## `project`

| Field | Type | Required | Nullable | Notes |
|---|---|---:|---:|---|
| `id` | integer | yes | no | id secuencial local del proyecto |
| `name` | string | yes | yes | nombre del proyecto |
| `cliente` | string | yes | yes | cliente |
| `ubicacion` | string | yes | yes | ubicación del proyecto |
| `ingeniero` | string | yes | yes | nombre de ingeniero |
| `codia` | string | yes | yes | CODIA |
| `empresa_calculo` | string | yes | yes | empresa calculista |
| `logo_empresa` | string | yes | yes | URL o referencia |
| `logo_cliente` | string | yes | yes | URL o referencia |
| `status` | enum | yes | no | `draft` o `calc_ready` |

### `project.status`
Valores válidos:
- `draft`
- `calc_ready`

## `validation`

| Field | Type | Required | Nullable | Notes |
|---|---|---:|---:|---|
| `critical_complete` | boolean | yes | no | derivado por validación |
| `missing_critical` | string[] | yes | no | rutas de campos críticos faltantes |
| `missing_non_critical` | string[] | yes | no | rutas de campos no críticos faltantes |
| `notes` | string[] | yes | no | observaciones de validación/normalización |

Reglas:
- `missing_*` usa rutas estables tipo `project.name`, `areas[0].catalog_type`
- `critical_complete` no es dato de usuario; se deriva

## `areas[]`
Cada área debe tener esta forma:

| Field | Type | Required | Nullable | Notes |
|---|---|---:|---:|---|
| `id` | string | yes | no | único por proyecto |
| `alias` | string | yes | no | nombre humano |
| `catalog_type` | string | yes | no | valor canónico resuelto desde catálogo |
| `catalog_sector` | string | yes | no | sector canónico del catálogo |
| `dimensions` | object | yes | no | ver reglas abajo |
| `people` | integer\|number\|null | yes | yes | opcional en v1 |
| `equipment_ids` | string[] | yes | no | puede estar vacío |
| `notes` | string[] | yes | no | observaciones |

## `areas[].dimensions`
Se aceptan dos formas de entrada, pero el objeto persistido debe quedar normalizado con valores derivados.

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
- `height_m` siempre requerido en ambas formas
- `volume_m3` debe existir luego de normalización
- si input trae `length_m` y `width_m`, se preservan
- si input trae solo `area_m2` y `height_m`, no se inventan `length_m` ni `width_m`

## `equipment[]`

| Field | Type | Required | Nullable | Notes |
|---|---|---:|---:|---|
| `id` | string | yes | no | único por proyecto |
| `alias` | string | yes | no | nombre humano |
| `kind` | string | yes | yes | tipo funcional de equipo |
| `cantidad` | integer\|number | yes | yes | fixed-only en v1 |
| `serves_area_ids` | string[] | yes | no | áreas servidas |
| `voltage` | string\|number\|null | yes | yes | placeholder |
| `frequency_hz` | number\|null | yes | yes | placeholder |
| `installation_type` | string\|null | yes | yes | placeholder |
| `power_w` | number\|null | yes | yes | placeholder |
| `power_kw` | number\|null | yes | yes | placeholder |
| `airflow_cfm` | number\|null | yes | yes | placeholder |
| `airflow_m3_h` | number\|null | yes | yes | placeholder |
| `notes` | string[] | yes | no | observaciones |

Reglas:
- lista `equipment` puede estar vacía en v1
- placeholders técnicos pueden ser `null`
- `cantidad` sigue política `fixed-only`

## `defaults_applied`
Lista de campos aplicados automáticamente.

Ejemplo:
```json
["ingeniero", "codia", "empresa_calculo"]
```

## Hybrid Area/Equipment Links
Relación explícita y consistente en dos direcciones:
- `areas[].equipment_ids`
- `equipment[].serves_area_ids`

Regla:
- si área referencia equipo, equipo debe referenciar área
- si equipo referencia área, área debe referenciar equipo

## Null-Present Policy
Para metadata y placeholders de v1:
- campo debe existir siempre
- si valor no está disponible, usar `null`
- no omitir campo por ausencia de dato

Ventaja:
- validadores más estables
- menos ambigüedad para calculador/spec/memory futuros

## Example Normalized Payload
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

## Lifecycle
- `draft`: faltan campos críticos
- `calc_ready`: todos los críticos completos

Regla:
- `calc_ready` no exige completar campos no críticos
