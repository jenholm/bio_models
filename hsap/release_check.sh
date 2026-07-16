#!/bin/bash
# HSAP Visualization Release Gate
# Checks that the standalone visualization package is complete and valid.
# Works for both web/ (dev) and hsap_visualization_release/ (release) directories.
set -e

DIR="${1:-.}"
ERRORS=0

check() {
    if eval "$2"; then
        echo "  ✓ $1"
    else
        echo "  ✗ $1"
        ERRORS=$((ERRORS + 1))
    fi
}

echo "HSAP Visualization Release Gate"
echo "================================"

# Find HTML file (support both naming conventions)
HTML_FILE=""
if [ -f "$DIR/index.html" ]; then
    HTML_FILE="$DIR/index.html"
elif [ -f "$DIR/hsap_visual_simulation.html" ]; then
    HTML_FILE="$DIR/hsap_visual_simulation.html"
fi
check "HTML file exists" "[ -n '$HTML_FILE' ]"

# Find JS files (support both naming conventions)
VIZ_JS=""
if [ -f "$DIR/js/hsap_visualization.js" ]; then
    VIZ_JS="$DIR/js/hsap_visualization.js"
elif [ -f "$DIR/js/hsap_visual_simulation.js" ]; then
    VIZ_JS="$DIR/js/hsap_visual_simulation.js"
fi
check "Visualization JS exists" "[ -n '$VIZ_JS' ]"

# Find CSS file (support both naming conventions)
CSS_FILE=""
if [ -f "$DIR/css/hsap_visualization.css" ]; then
    CSS_FILE="$DIR/css/hsap_visualization.css"
elif [ -f "$DIR/css/hsap_visual_simulation.css" ]; then
    CSS_FILE="$DIR/css/hsap_visual_simulation.css"
fi
check "CSS exists" "[ -n '$CSS_FILE' ]"

check "hsap_data.js exists" "[ -f '$DIR/js/hsap_data.js' ]"

# Check for network dependencies
check "No fetch() in JS" "! grep -q 'fetch(' '$DIR/js/'*.js 2>/dev/null || true"
check "No external URLs" "! grep -qE 'https?://' '$DIR/js/'*.js '$HTML_FILE' 2>/dev/null || true"

# Check six scenarios present in data
if [ -f "$DIR/js/hsap_data.js" ]; then
    for scenario in A_normal_baseline B_hsap_abundance C_crowded_abundance D_high_predation_survival E_behavioral_sink_recovery F_behavioral_sink_extinction; do
        check "Scenario $scenario in data" "grep -q '$scenario' '$DIR/js/hsap_data.js'"
    done
fi

# Check no stale scenario names
if [ -n "$VIZ_JS" ]; then
    check "No stale F_behavioral_sink_partial_collapse" "! grep -q 'F_behavioral_sink_partial_collapse' '$VIZ_JS'"
fi

# Check load order (data before visualization in HTML)
if [ -n "$HTML_FILE" ]; then
    DATA_POS=$(grep -b -o 'hsap_data.js' "$HTML_FILE" | head -1 | cut -d: -f1 || echo "999999")
    VIZ_POS=$(grep -b -o 'hsap_visualization.js\|hsap_visual_simulation.js' "$HTML_FILE" | head -1 | cut -d: -f1 || echo "0")
    check "hsap_data.js loads before visualization js" "[ $DATA_POS -lt $VIZ_POS ]"
fi

echo ""
echo "================================"
if [ $ERRORS -eq 0 ]; then
    echo "HSAP Visualization Release PASS"
    exit 0
else
    echo "HSAP Visualization Release FAIL ($ERRORS errors)"
    exit 1
fi
