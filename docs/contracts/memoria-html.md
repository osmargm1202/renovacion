# Contract: memoria.html

## Purpose
Memoria de cálculo HTML document - complete calculation report for air renovation projects.

## Location
`/proyectos/[id]/memoria.html`

## Inputs Required
- `/proyectos/[id]/input.json` (project metadata + areas + equipment)
- `/proyectos/[id]/resultados.json` (calculation results)
- `/proyectos/[id]/spec.json` (equipment selection + alternatives)
- Project assets in `/proyectos/[id]/assets/`

## Document Structure

### Section IDs (stable HTML anchors)
1. `portada` - Cover page
2. `indice` - Table of contents
3. `teoria-calculo` - Calculation theory
4. `resultados-calculo` - Calculation results
5. `seleccion-equipos` - Equipment selection
6. `fin` - Closing section

### Required Content by Section

#### 1. Portada (Cover Page)
**Mandatory fields:**
- Company logo (`logo_empresa`)
- Client logo (`logo_cliente`)
- Project name
- Location (`ubicacion`)
- Engineer (`ingeniero`)
- CODIA number
- Calculation company (`empresa_calculo`)
- Date (generation timestamp)

**Layout:** Center-aligned, full-page branding layout

#### 2. Índice (Table of Contents)
**Content:**
- Linked list to all section anchors (#portada, #teoria-calculo, etc.)
- Clean, printable layout
- HTML-friendly structure (no PDF page numbers yet)

#### 3. Teoría de Cálculo (Calculation Theory)
**Content:**
- Base theory: air renovation fundamentals
- RH method explanation (renovations/hour)
- People method explanation (airflow per person)
- Dynamic inserts: methods actually used in project
- Policy references: midpoint, max-of-both, round-2-decimals

**Formula rendering:** KaTeX/LaTeX for equations

#### 4. Resultados de Cálculo (Calculation Results)
**Content:**
- Global project summary (`summary` from resultados.json)
- Breakdown by area (`area_results[]`)
- Governing method per area
- Formula traces (structured → KaTeX, fallback to human trace)
- Show both RH and people blocks even when people N/A

**Formula policy:** hybrid (structured trace → KaTeX, else human trace)

#### 5. Selección de Equipos (Equipment Selection)
**Content per equipment:**
- Equipment alias
- Required airflow (m³/h)
- Selected model (brand, model, specs)
- Electrical data (voltage, power, frequency)
- Installation type
- Equipment image or placeholder
- **Alternatives ALWAYS shown** (policy: `always`)
- Explicit block if selection failed

**Asset policy:** Local project assets or placeholder

#### 6. Fin (Closing)
**Content:**
- Document closure
- Technical footer
- Consistent layout

## HTML/CSS Rules

### Typography
- Base font: **Arial, sans-serif**
- Font sizes defined in CSS
- Line-height optimized for readability and print

### CSS Structure
- `assets/css/memoria.css` - Global shared CSS
- `assets/css/memoria-sections.css` - Section-specific CSS
- Inline embedded CSS in final HTML (no external stylesheet dependencies)
- KaTeX CSS included for formula rendering

### Responsive/Print
- Layout optimized for letter-size print
- Page breaks controlled via CSS
- Print media queries included

## Formula Rendering

### Policy: `hybrid`
1. **If structured trace exists** → Convert to KaTeX/LaTeX formula
2. **Else** → Render human trace as fallback

### Required formulas
- RH method: `Q_rh = V × RH`
- People method: `Q_people = N × caudal_persona`

### KaTeX Integration
- Include KaTeX library via CDN
- Render formulas server-side or inline
- Fallback to plain text if rendering fails

## Asset Staging

### Pre-render steps
1. Ensure `/proyectos/[id]/assets/` exists
2. Resolve cover logos:
   - If URL → Download to `/proyectos/[id]/assets/logos/`
   - If local path → Copy to assets
3. Resolve equipment images:
   - Check project assets first
   - Fall back to catalog reference (`image_asset` from spec.json)
   - If missing → Use placeholder image

### Asset Policy: `project+catalog-assets`
- Prefer project-local assets
- Use catalog assets as fallback
- Always use local paths in final HTML (no external URLs)

### Asset Failure Policy: `continue-placeholder`
- Missing image → Use placeholder
- Never abort rendering due to missing asset

## Alternatives Rendering

### Policy: `always`
- Show alternatives even when selection succeeded
- Display side-by-side or in table format
- Highlight selected model vs alternatives

## Error Model

### Status: `completed`
- All sections rendered
- Assets staged successfully
- `memoria.html` written to disk

### Status: `needs_input`
- Missing critical metadata (project name, engineer, etc.)
- Cannot resolve from defaults

### Status: `blocked`
- Missing required JSON files (input/resultados/spec)
- Tooling/render engine not available

### Status: `failed`
- Hard render error
- Contract mismatch between JSON artifacts
- Critical asset staging failure (e.g., filesystem error)

## Output Format

### File
- Single self-contained HTML file
- Embedded CSS (inline in `<style>` tag)
- Local asset references only
- UTF-8 encoding
- Pretty-printed HTML (readable source)

### Size
- Target: < 500KB for typical project
- Images embedded via local paths (not base64)

## Testing Requirements

### Template Tests
- All section IDs present
- Índice links point to valid anchors

### Asset Tests
- Remote logo downloads to project assets
- Missing image renders placeholder without error

### Formula Tests
- Structured trace → valid KaTeX block
- Fallback to human trace works

### Content Tests
- Results include summary + area breakdown
- Equipment section includes model + alternatives

### Integration Test
- Process proyecto 1:
  - Input: `proyectos/1/input.json`
  - Results: `proyectos/1/resultados.json`
  - Spec: `proyectos/1/spec.json`
  - Output: `proyectos/1/memoria.html`
- Expected: E1 extractor with EX-150 selected + 3 alternatives

## Expected Output for AURORA GMR (Project 1)

### Portada
- ORGM logo
- BOHC logo
- Title: "AURORA GMR"
- Location: Distrito Nacional
- Engineer: Osmar Garcia
- CODIA: 36467

### Resultados
- Area A1: Baño principal
- RH method: 129.6 m³/h
- Formula: Q_rh = 21.60 × 6.00 = 129.60 m³/h

### Selección
- Equipment E1: Extractor baño principal
- Selected: EX-150 (140 m³/h)
- Alternatives: EX-160, EX-200, EX-250

## Version
Contract v1.0
