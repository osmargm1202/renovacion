# Contract: Memory Assets

## Purpose
Asset management policy for memoria generation - staging, downloading, fallback, and referencing.

## Asset Locations

### Project Assets Directory
`/proyectos/[id]/assets/`

Subdirectories:
- `logos/` - Company and client logos
- `equipos/` - Equipment images
- `placeholders/` - Fallback placeholder images

### Catalog Assets (read-only reference)
`assets/extractores/` - Extractor equipment images from catalog
`assets/inyectores/` - Injector equipment images from catalog
`assets/placeholders/` - Global placeholder images

## Asset Types

### 1. Logos (Portada)

**Sources:**
- `project.logo_empresa` (URL or local path)
- `project.logo_cliente` (URL or local path)

**Staging rules:**
1. If URL → Download to `/proyectos/[id]/assets/logos/[filename]`
2. If local path → Copy to `/proyectos/[id]/assets/logos/[filename]`
3. If download fails → Use placeholder logo
4. If missing → Use default company logo

**Expected formats:** PNG, JPG, SVG
**Max dimensions:** 2.5in × 1.5in (CSS controlled)

### 2. Equipment Images

**Sources:**
- `spec.json`: `equipment_specs[].selected_model.image_asset`
- `spec.json`: `equipment_specs[].alternatives[].image_asset`

**Staging rules:**
1. Check `/proyectos/[id]/assets/equipos/[filename]` first (project-specific)
2. If not found, resolve from catalog reference (e.g., `assets/extractores/ex-150.png`)
3. Copy catalog asset to `/proyectos/[id]/assets/equipos/` for self-containment
4. If asset missing → Use placeholder image

**Expected formats:** PNG, JPG
**Recommended size:** 400×300px (CSS will scale)

### 3. Placeholder Images

**Types:**
- `placeholder-logo.png` - Generic logo placeholder
- `placeholder-equipment.png` - Generic equipment placeholder

**Location:** `/proyectos/[id]/assets/placeholders/`

**Fallback chain:**
1. Project placeholder
2. Global catalog placeholder
3. Inline SVG placeholder (last resort)

## Asset Policies

### Policy: `project+catalog-assets`
- **Prefer:** Project-local assets (`/proyectos/[id]/assets/`)
- **Fallback:** Catalog assets (`assets/extractores/`, etc.)
- **Copy:** Always copy catalog assets to project assets for self-containment

### Policy: `continue-placeholder`
- **Missing asset:** Never abort rendering
- **Action:** Substitute placeholder image
- **Log:** Warn about missing asset but continue

### Policy: `always-local`
- **Final HTML:** Reference only local paths
- **No external URLs** in final document
- **Self-contained:** Document + assets folder = portable package

## Asset Staging Workflow

### Pre-render Phase
```
1. Ensure /proyectos/[id]/assets/ structure exists
   ├── logos/
   ├── equipos/
   └── placeholders/

2. Stage logos:
   - Download/copy empresa logo
   - Download/copy cliente logo

3. Stage equipment images:
   - For each equipment in spec.json:
     - Resolve selected_model.image_asset
     - Resolve alternatives[].image_asset
     - Copy to /proyectos/[id]/assets/equipos/

4. Stage placeholders:
   - Copy global placeholders to project
```

### Asset Resolution Function

**Signature:**
```javascript
resolveAsset(assetRef, assetType, projectId)
```

**Parameters:**
- `assetRef`: URL or path from JSON
- `assetType`: 'logo' | 'equipment' | 'placeholder'
- `projectId`: Project ID number

**Returns:**
- Local path relative to memoria.html (e.g., `assets/equipos/ex-150.png`)

**Behavior:**
1. If URL → Download to project assets
2. If catalog reference → Copy to project assets
3. If local project path exists → Return as-is
4. If resolution fails → Return placeholder path

## Asset Download

### HTTP/HTTPS URLs

**Supported:**
- PNG, JPG, JPEG, SVG
- Max download size: 5MB
- Timeout: 10 seconds

**On failure:**
- Log warning
- Return placeholder
- Continue rendering

### File Copy

**Supported:**
- Copy from catalog to project assets
- Verify file exists before copy
- Preserve original filename

**On failure:**
- Log warning
- Return placeholder
- Continue rendering

## Asset References in HTML

### Logo in Portada
```html
<img src="assets/logos/orgm.png" alt="Logo ORGM" class="portada-logo">
```

### Equipment Image in Selección
```html
<img src="assets/equipos/ex-150.png" alt="EX-150" class="equipment-image">
```

### Placeholder Fallback
```html
<img src="assets/placeholders/placeholder-equipment.png" alt="Equipment image not available" class="equipment-image placeholder">
```

## Placeholder Specifications

### Logo Placeholder
- **Dimensions:** 200×100px
- **Background:** Light gray (#f0f0f0)
- **Text:** "Logo" in center
- **Format:** PNG with transparency

### Equipment Placeholder
- **Dimensions:** 400×300px
- **Background:** Light gray (#f5f5f5)
- **Text:** "Image not available" in center
- **Icon:** Optional generic equipment icon
- **Format:** PNG

## Testing Requirements

### Asset Staging Tests
1. **Download URL logo** → Appears in `/proyectos/[id]/assets/logos/`
2. **Copy catalog equipment image** → Appears in `/proyectos/[id]/assets/equipos/`
3. **Missing asset** → Placeholder used, rendering continues
4. **Invalid URL** → Timeout handled, placeholder substituted

### Asset Reference Tests
1. **HTML references local paths** → No external URLs in final document
2. **Relative paths work** → Opening HTML loads all assets correctly
3. **Placeholder renders** → Fallback image displays properly

### Self-containment Test
1. Copy `/proyectos/[id]/` folder to new location
2. Open `memoria.html`
3. **Expected:** All logos and equipment images load correctly

## Error Model

### Warnings (non-blocking)
- Failed to download logo from URL
- Equipment image not found in catalog
- Asset copy failed

### Errors (blocking, should not happen with continue-placeholder)
- Cannot create `/proyectos/[id]/assets/` directory (filesystem error)
- Cannot write placeholder image (disk full)

## Asset Manifest (optional future feature)

### `proyectos/[id]/assets/manifest.json`
```json
{
  "logos": [
    {
      "type": "empresa",
      "source": "https://r2.or-gm.com/orgm.png",
      "local": "assets/logos/orgm.png",
      "status": "downloaded"
    }
  ],
  "equipment": [
    {
      "equipment_id": "E1",
      "model": "EX-150",
      "source": "assets/extractores/ex-150.png",
      "local": "assets/equipos/ex-150.png",
      "status": "copied"
    }
  ]
}
```

## Best Practices

1. **Always copy catalog assets to project** - Don't rely on catalog paths in final HTML
2. **Validate downloads** - Check file size > 0 and format is valid
3. **Use placeholders liberally** - Never break rendering due to missing image
4. **Log asset operations** - Track what was downloaded/copied for debugging
5. **Test self-containment** - Ensure project folder is portable

## Version
Contract v1.0
