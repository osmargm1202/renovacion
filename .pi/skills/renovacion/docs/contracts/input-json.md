# Input JSON Contract

## Purpose

`input.json` es artefacto base por proyecto para flujo demand-only de solo áreas/necesidad. Guarda metadata, validación y áreas necesarias para cálculo por defecto. Datos de equipos quedan como compatibilidad futura/manual.

Ruta:

- `./proyectos/[id]/input.json` en la carpeta de ejecución actual

`[id]` puede ser entero local (`1`) o slug seguro (`miniso-pr`) compuesto por letras, números, puntos, guiones bajos y guiones. No se permiten rutas ni separadores.

## Top-level shape

```json
{
  "project": {},
  "validation": {},
  "areas": [],
  "defaults_applied": []
}
```

Compatibilidad:

- no agregar otras llaves top-level en v1
- metadata faltante se persiste como `null`, no se omite
- `equipment` opcional: puede omitirse en flujo demand-only o mantenerse para compatibilidad/manual scope

## `project`

| Field             | Type    | Required | Nullable | Notes                  |
| ----------------- | ------- | -------: | -------: | ---------------------- |
| `id`              | integer\|string |      yes |       no | id local secuencial o slug seguro    |
| `name`            | string  |      yes |      yes | nombre proyecto        |
| `cliente`         | string  |      yes |      yes | cliente                |
| `ubicacion`       | string  |      yes |      yes | ubicación              |
| `ingeniero`       | string  |      yes |      yes | ingeniero              |
| `codia`           | string  |      yes |      yes | CODIA                  |
| `empresa_calculo` | string  |      yes |      yes | empresa calculista     |
| `logo_empresa`    | string  |      yes |      yes | URL o referencia       |
| `logo_cliente`    | string  |      yes |      yes | URL o referencia       |
| `status`          | enum    |      yes |       no | `draft` o `calc_ready` |

## `validation`

| Field                  | Type     | Required | Nullable | Notes                    |
| ---------------------- | -------- | -------: | -------: | ------------------------ |
| `critical_complete`    | boolean  |      yes |       no | derivado                 |
| `missing_critical`     | string[] |      yes |       no | rutas faltantes          |
| `missing_non_critical` | string[] |      yes |       no | rutas faltantes          |
| `notes`                | string[] |      yes |       no | validación/normalización |

## `areas[]`

Marcadores rápidos de contrato:

- `| `extractor_type` | enum | no |`
- `| `equipment_ids` | string[] | no |`

| Field            | Type                  | Required | Nullable | Notes                                              |
| ---------------- | --------------------- | -------: | -------: | -------------------------------------------------- |
| `id`             | string                |      yes |       no | único por proyecto                                 |
| `alias`          | string                |      yes |       no | nombre humano                                      |
| `catalog_type`   | string                |      yes |       no | valor canónico                                     |
| `catalog_sector` | string                |      yes |       no | `terciario`, `industrial`, `residencial_domestico` |
| `extractor_type` | enum                  |       no |       no | opcional para future/manual equipment scope        |
| `dimensions`     | object                |      yes |       no | ver abajo                                          |
| `people`         | integer\|number\|null |      yes |      yes | opcional v1                                        |
| `equipment_ids`  | string[]              |       no |       no | opcional; ignorado por calc demand-only            |
| `notes`          | string[]              |      yes |       no | observaciones                                      |

### `areas[].extractor_type`

Valores válidos cuando existe:

- `sencillo`
- `ducteable`

Política:

- no se exige `extractor_type` para flujo default demand-only
- si existe, describe categoría de uso para future/manual equipment scope
- no inferir desde capacidad, CFM o m³/h

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

## `equipment[]` (optional)

Payload opcional para compatibilidad hacia atrás o future/manual equipment scope.
Puede omitirse completo o enviarse vacío en flujo demand-only.

| Field               | Type                 | Required when item exists | Nullable | Notes              |
| ------------------- | -------------------- | ------------------------: | -------: | ------------------ |
| `id`                | string               |                       yes |       no | único por proyecto |
| `alias`             | string               |                       yes |       no | nombre humano      |
| `kind`              | string               |                       yes |      yes | tipo funcional     |
| `cantidad`          | integer\|number      |                       yes |      yes | fixed-only v1      |
| `serves_area_ids`   | string[]             |                       yes |       no | áreas servidas     |
| `voltage`           | string\|number\|null |                       yes |      yes | placeholder        |
| `frequency_hz`      | number\|null         |                       yes |      yes | placeholder        |
| `installation_type` | string\|null         |                       yes |      yes | placeholder        |
| `power_w`           | number\|null         |                       yes |      yes | placeholder        |
| `power_kw`          | number\|null         |                       yes |      yes | placeholder        |
| `airflow_cfm`       | number\|null         |                       yes |      yes | placeholder        |
| `airflow_m3_h`      | number\|null         |                       yes |      yes | placeholder        |
| `notes`             | string[]             |                       yes |       no | observaciones      |

## `defaults_applied`

Lista de campos aplicados automáticamente.

## Optional area/equipment links

Relación solo para compatibilidad/manual scope:

- `areas[].equipment_ids`
- `equipment[].serves_area_ids`

Si alguno falta, validación demand-only no bloquea `calc_ready`.

## Example normalized payload (demand-only)

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
    "missing_non_critical": ["areas[0].people"],
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

## Backward-compatible example notes

- inputs viejos pueden conservar `equipment`
- inputs viejos pueden conservar `areas[].extractor_type`
- inputs viejos pueden conservar `areas[].equipment_ids`
- calc demand-only ignora esos campos en `resultados.json`
