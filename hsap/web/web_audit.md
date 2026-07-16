# HSAP Web Visualization — Architecture Audit

## Current Architecture

```
web/
├── hsap_visual_simulation.html          (3.4 KB)  — Single-page app entry
├── css/
│   └── hsap_visual_simulation.css       (7.7 KB)  — Dark theme, 4-col grid layout
├── js/
│   └── hsap_visual_simulation.js        (34.7 KB) — All visualization logic (896 lines)
└── data/
    ├── A_normal_baseline.json           (19.7 MB) — 501 frames
    ├── B_hsap_abundance.json            (19.7 MB) — 501 frames
    ├── C_crowded_abundance.json         (19.7 MB) — 501 frames
    ├── D_high_predation_survival.json   (19.7 MB) — 501 frames
    ├── E_behavioral_sink_recovery.json  (19.6 MB) — 501 frames
    └── F_behavioral_sink_extinction.json (4.1 MB)  — 457 frames (early extinction)
```

**Total data size:** ~103 MB (JSON)

## External Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| None | CDN/npm | ✅ No external JS/CSS libraries |
| None | Font CDN | ✅ Uses system fonts only |
| None | API calls | ✅ No runtime API calls |

**The application has zero external runtime dependencies.** All code is vanilla HTML/CSS/JS with Canvas 2D rendering.

## Runtime Network Calls

| Call | Location | Issue |
|------|----------|-------|
| `fetch('data/A_normal_baseline.json')` | `loadTraces()` :22-31 | ❌ FAILS on `file://` |
| `fetch('data/B_hsap_abundance.json')` | `loadTraces()` :22-31 | ❌ FAILS on `file://` |
| `fetch('data/C_crowded_abundance.json')` | `loadTraces()` :22-31 | ❌ FAILS on `file://` |
| `fetch('data/D_high_predation_survival.json')` | `loadTraces()` :22-31 | ❌ FAILS on `file://` |
| `fetch('data/E_behavioral_sink_recovery.json')` | `loadTraces()` :22-31 | ❌ FAILS on `file://` |
| `fetch('data/F_behavioral_sink_extinction.json')` | `loadTraces()` :22-31 | ❌ FAILS on `file://` |

**Critical issue:** Browsers block `fetch()` from `file://` URLs due to CORS. Double-clicking `index.html` shows blank loading screen.

## Server Path Assumptions

1. All data loaded via relative `data/` path — works with HTTP server, fails with `file://`
2. CSS loaded via relative `css/` path — works with both `file://` and HTTP
3. JS loaded via relative `js/` path — works with both `file://` and HTTP
4. No `<base>` tag or absolute paths

## Scenario Name Mismatch

**CRITICAL BUG:** The JS `WORLDS` constant uses:

```js
const WORLDS = [..., 'F_behavioral_sink_partial_collapse'];
```

But the actual data file is named:

```
web/data/F_behavioral_sink_extinction.json
```

The `F_behavioral_sink_partial_collapse` JSON file does NOT exist in `web/data/`. The HTML `<select>` correctly references `F_behavioral_sink_extinction`. This means:

- The `<select>` dropdown shows `F_behavioral_sink_extinction` (correct)
- But `loadTraces()` tries to `fetch('data/F_behavioral_sink_partial_collapse.json')` (wrong)
- The comparison mode uses `WORLDS` constant and also looks up `F_behavioral_sink_partial_collapse`
- Scenario F will never load properly in JS

## Browser Compatibility

| Feature | Chrome | Firefox | Edge | Safari |
|---------|--------|---------|------|--------|
| Canvas 2D | ✅ | ✅ | ✅ | ✅ |
| `fetch()` (HTTP) | ✅ | ✅ | ✅ | ✅ |
| `fetch()` (file://) | ❌ | ❌ | ❌ | ❌ |
| `structuredClone` | N/A | N/A | N/A | N/A |
| ES6 modules | N/A | N/A | N/A | N/A |
| `Array.reduce` | ✅ | ✅ | ✅ | ✅ |
| Template literals | ✅ | ✅ | ✅ | ✅ |

**No compatibility issues for modern browsers.** The code uses only widely-supported ES6 features.

## Conversion Requirements

### Must Fix
1. **Embed all JSON data** into a single JS file (`hsap_data.js`) so no `fetch()` is needed
2. **Fix WORLDS constant** — change `F_behavioral_sink_partial_collapse` → `F_behavioral_sink_extinction`
3. **Update `loadTraces()`** — make it synchronous, read from `HSAP_DATA` global

### Should Fix
4. **Add meta block** to each JSON frame set (model version, git commit, generation date)
5. **Repair scientific language** — avoid causal overclaiming
6. **Add About panel** with model description and citations

### Nice to Have
7. **Create standalone release package** — self-contained zip
8. **Add validation script** to check data consistency
9. **Create export pipeline** for reproducing visualization from model runs

## Data Flow (Current vs Target)

### Current
```
Python model → export_visual_trace.py → web/data/*.json → fetch() → JS visualization
                                                    ↑
                                              BROKEN on file://
```

### Target
```
Python model → export_visualization_data.py → web/js/hsap_data.js (embedded)
                                                        ↓
                                              JS visualization (standalone)
```
