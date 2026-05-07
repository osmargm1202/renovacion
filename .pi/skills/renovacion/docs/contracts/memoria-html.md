# Contract: memoria.html

## Purpose

Memoria HTML final de cálculo y necesidad de renovación de aire por área. Este contrato es demand-only: documenta demanda calculada, no selección comercial de equipos.

## Location

`./proyectos/[id]/memoria.html` en la carpeta de ejecución actual

`[id]` puede ser numérico o slug seguro como `miniso-pr`.

## Inputs required

- `input.json`
- `resultados.json`
- `assets/` del proyecto

## Required sections

1. `portada`
2. `indice`
3. `teoria-calculo`
4. `resultados-calculo`
5. `resumen-necesidad-area`
6. `fin`

## Resumen de Necesidad por Área

Contenido requerido por área:

- id de área
- alias de área
- método gobernante
- caudal requerido final en `m3/h`
- caudal requerido final en `CFM`
- números con miles separados por coma y dos decimales: `1,000.00`

Salida visible esperada:

- título `Resumen de Necesidad por Área`
- tabla o bloque equivalente con valores por área
- para AURORA GMR área EX3: `2,448.00 m3/h` y `1,440.84 CFM`

## Content exclusions

Default memory output must not show:

- `Equipos Requeridos`
- `Selección de Equipos`
- fichas comerciales de equipos
- modelo seleccionado
- alternativas comerciales
- datos eléctricos de equipos comerciales

## Asset policy

- usar assets locales del proyecto
- sin CDN ni URLs externas en HTML final
- fórmulas usan KaTeX vendorizado local

## Expected output for AURORA GMR project 1

### Resultados

- área A1: Baño principal
- RH: `129.6 m³/h`

### Resumen demand-only

- área A1: Baño principal
- requerido: `129.60 m3/h`
- requerido: `76.28 CFM`
- no aparece `Selección de Equipos`
