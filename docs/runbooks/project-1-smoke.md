# Project 1 Smoke Test Runbook

## Purpose
Quick validation that the memoria generation pipeline works end-to-end for project 1 (AURORA GMR).

## Prerequisites

### Required
- Node.js (for memory-engine)
- Repository cloned locally
- Working directory: repository root

### Expected Files
- `proyectos/1/input.json` - Project input data
- `proyectos/1/resultados.json` - Calculation results
- `proyectos/1/spec.json` - Equipment specifications
- `lib/memory-engine/*` - Memory engine implementation
- `assets/vendor/katex/*` - Vendored KaTeX assets
- `assets/css/*` - CSS stylesheets

## Command

```bash
bash scripts/run-project-1.sh
```

Or with explicit path:

```bash
cd /path/to/renovacion
bash scripts/run-project-1.sh
```

## Expected Output

### Console Output
```
==========================================
Project 1 Smoke Test - AURORA GMR
==========================================

Checking preconditions...
✅ Preconditions OK

Step 1/3: Checking calc-engine outputs...
✅ resultados.json exists

Step 2/3: Checking spec-engine outputs...
✅ spec.json exists

Step 3/3: Running memory-engine...
Memory Engine Runner
====================
Project ID: 1
Project Path: proyectos/1

Generating memoria.html...
✅ Success! (0.03s)
Output: proyectos/1/memoria.html
✅ memoria.html generated

Validating outputs...
✅ Content validation passed

==========================================
✅ SMOKE TEST PASSED
==========================================

Outputs:
  - proyectos/1/resultados.json
  - proyectos/1/spec.json
  - proyectos/1/memoria.html
  - proyectos/1/assets/

Memoria is offline-capable (vendored KaTeX)
```

### Generated Files
- `proyectos/1/memoria.html` (~25KB)
- `proyectos/1/assets/logos/empresa-orgm.png`
- `proyectos/1/assets/logos/cliente-bohc.png`
- `proyectos/1/assets/equipos/ex-*.png`
- `proyectos/1/assets/placeholders/*.svg`

## Verification Checklist

### Quick Check
1. ✅ Script exits with code 0 (success)
2. ✅ `memoria.html` exists
3. ✅ No error messages in output

### Content Verification
Open `proyectos/1/memoria.html` in browser and verify:

1. **Portada (Cover Page)**
   - [ ] ORGM logo visible
   - [ ] BOHC logo visible
   - [ ] Project name: "AURORA GMR"
   - [ ] Client: "BOHC SRL"
   - [ ] Engineer: "Osmar Garcia"
   - [ ] CODIA: "36467"

2. **Índice (Table of Contents)**
   - [ ] All 6 sections linked
   - [ ] Links are clickable and navigate correctly

3. **Teoría de Cálculo**
   - [ ] RH method explained
   - [ ] People method explained
   - [ ] Policies displayed (midpoint, max-of-both, round-2-decimals)

4. **Resultados de Cálculo**
   - [ ] Summary shows 129.6 m³/h total
   - [ ] Area A1 "Baño principal" present
   - [ ] Formula rendered (KaTeX or text)
   - [ ] Governing method: RH

5. **Selección de Equipos**
   - [ ] Equipment E1 "Extractor baño principal"
   - [ ] Selected model: EX-150 (140 m³/h)
   - [ ] Alternatives shown: EX-160, EX-200, EX-250
   - [ ] Equipment image or placeholder visible

6. **Fin (Closing)**
   - [ ] Document closure text
   - [ ] Signature block with engineer name and CODIA

### Offline Capability
1. **Disconnect from internet**
2. **Open `proyectos/1/memoria.html` in browser**
3. **Verify:**
   - [ ] Page loads completely
   - [ ] Logos display
   - [ ] Formulas render (KaTeX loaded locally)
   - [ ] No broken assets or missing styles

### Technical Validation
```bash
# No CDN references
grep -i "cdn\|jsdelivr\|unpkg" proyectos/1/memoria.html
# Should return nothing (exit code 1)

# Uses vendored KaTeX
grep "assets/vendor/katex" proyectos/1/memoria.html
# Should show local KaTeX paths

# Check file size
ls -lh proyectos/1/memoria.html
# Should be ~25KB
```

## Troubleshooting

### Script fails with "Missing input.json"
**Cause:** Project 1 input file not present  
**Fix:** Ensure `proyectos/1/input.json` exists and is valid JSON

### Script fails with "Missing resultados.json"
**Cause:** Calculation results not generated  
**Fix:** Run calc-engine to generate results, or ensure file exists from baseline

### Script fails with "Missing spec.json"
**Cause:** Equipment specifications not generated  
**Fix:** Run spec-engine to generate specs, or ensure file exists from baseline

### Script fails with "Node.js not found"
**Cause:** Node.js not installed or not in PATH  
**Fix:** Install Node.js 16+ and ensure `node` command is available

### memoria.html contains CDN references
**Cause:** Memory engine not updated to use vendored KaTeX  
**Fix:** Check `lib/memory-engine/formula.js` uses local paths, regenerate

### Formulas don't render in browser
**Cause:** KaTeX assets not vendored or paths incorrect  
**Fix:**
1. Verify `assets/vendor/katex/` contains katex.min.{css,js}, auto-render.min.js, fonts/
2. Check browser console for 404 errors on KaTeX assets
3. Verify relative paths from `proyectos/1/memoria.html` to `assets/vendor/katex/` are correct

### Logos or equipment images missing
**Cause:** Assets not staged or remote download failed  
**Fix:**
1. Check `proyectos/1/assets/` directory exists
2. Run memory-engine runner again to re-attempt asset staging
3. Check warnings in memory-engine output for failed downloads

## Success Criteria

Smoke test is successful when:
- [x] Script exits with code 0
- [x] `memoria.html` generated
- [x] Content validation passes (AURORA GMR, 129.6 m³/h, EX-150 present)
- [x] No CDN references in HTML
- [x] Vendored KaTeX referenced
- [x] HTML opens in browser without internet
- [x] All sections visible and complete
- [x] Formulas render correctly

## Baseline State

### Expected Commit Artifacts
After successful smoke test, repository baseline includes:
- `proyectos/1/input.json` (project definition)
- `proyectos/1/resultados.json` (calculation results)
- `proyectos/1/spec.json` (equipment specs)
- `proyectos/1/memoria.html` (generated report)
- `proyectos/1/assets/*` (staged logos, equipment images, placeholders)
- `assets/vendor/katex/*` (vendored KaTeX library)
- All engine implementations in `lib/`
- All tests in `tests/`
- All contracts in `docs/contracts/`

### Not Included in Baseline
- Temporary files (`__pycache__`, `.pyc`)
- Session data (`.pi/agent-sessions/`)
- Obsolete test artifacts
- Intermediate noise files

## Notes

- **Version:** HTML v1 hardening baseline
- **Date:** 2026-04-25
- **Project:** AURORA GMR (Project 1)
- **Pipeline:** input-validation → calc-engine → spec-engine → memory-engine
- **Offline-capable:** Yes (vendored KaTeX)
- **Dependencies:** Node.js only (Python engines run separately in full pipeline)
