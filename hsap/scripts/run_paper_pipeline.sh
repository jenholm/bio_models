#!/usr/bin/env bash
# Sequential runner for the full paper pipeline.
# Tracks progress in results/paper/.pipeline_status.json for resilience.
# Re-run after interruption: completed tasks are skipped.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STATUS_FILE="$PROJECT_DIR/results/paper/.pipeline_status.json"

# ── Task definitions (in order) ──
TASKS=(
  "paper-set1:Set1 HSAP comparison (4 worlds, 50 seeds, ~30 min)"
  "paper-set2:Set2 behavioral sink (3 worlds, 50 seeds, ~30 min)"
  "paper-set3:Set3 factorial grid (54 scenarios, 30 seeds, ~8 hr)"
  "null-ablation:Null model + ablation suite (~30 min)"
  "ga:GA searches (3 searches, ~6 hr)"
  "sensitivity:Morris + Sobol sensitivity (~3 hr)"
  "figures:Generate paper figures (~1 min)"
  "report:Generate final report (<1 sec)"
)

# Commands for each task
declare -A CMDS
CMDS[paper-set1]="python3 $SCRIPT_DIR/run_paper_experiments.py --seeds 50 --sets Set1_HSAP_comparison"
CMDS[paper-set2]="python3 $SCRIPT_DIR/run_paper_experiments.py --seeds 50 --sets Set2_behavioral_sink"
CMDS[paper-set3]="python3 $SCRIPT_DIR/run_paper_experiments.py --seeds 30 --sets Set3_factorial"
CMDS[null-ablation]="python3 $SCRIPT_DIR/run_null_ablation_suite.py --figures"
CMDS[ga]="python3 $SCRIPT_DIR/run_paper_ga.py"
CMDS[sensitivity]="python3 $SCRIPT_DIR/run_paper_sensitivity.py --sobol-samples 256"
CMDS[figures]="python3 $SCRIPT_DIR/make_paper_figures.py --dpi 300"
CMDS[report]="python3 $SCRIPT_DIR/make_report.py"

# ── Status file helpers ──
init_status() {
  mkdir -p "$(dirname "$STATUS_FILE")"
  if [ ! -f "$STATUS_FILE" ]; then
    echo '{' > "$STATUS_FILE"
    local first=true
    for entry in "${TASKS[@]}"; do
      local name="${entry%%:*}"
      $first || echo ',' >> "$STATUS_FILE"
      first=false
      cat >> "$STATUS_FILE" <<EOF
  "$name": {"status": "pending", "started": null, "completed": null, "elapsed_sec": null}
EOF
    done
    echo '' >> "$STATUS_FILE"
    echo '}' >> "$STATUS_FILE"
    echo "Initialized status file: $STATUS_FILE"
  fi
}

set_status() {
  local task="$1" field="$2" value="$3"
  python3 -c "
import json, sys
p = '$STATUS_FILE'
with open(p) as f: d = json.load(f)
d['$task']['$field'] = $value
with open(p, 'w') as f: json.dump(d, f, indent=2)
"
}

get_status() {
  local task="$1"
  python3 -c "
import json
with open('$STATUS_FILE') as f: d = json.load(f)
print(d['$task']['status'])
"
}

# ── Run one task with timing ──
run_task() {
  local entry="$1"
  local name="${entry%%:*}"
  local desc="${entry#*:}"

  local current_status
  current_status=$(get_status "$name")

  if [ "$current_status" = "completed" ]; then
    echo ""
    echo "  ⏭️  $name already completed. Skipping."
    return 0
  fi

  echo ""
  echo "═══════════════════════════════════════════════════════════════"
  echo "  START: $name — $desc"
  echo "  $(date)"
  echo "═══════════════════════════════════════════════════════════════"
  echo ""

  set_status "$name" "status" '"running"'
  set_status "$name" "started" "\"$(date -Iseconds)\""

  local start_epoch
  start_epoch=$(date +%s)

  cd "$PROJECT_DIR"
  if eval "${CMDS[$name]}"; then
    local elapsed=$(( $(date +%s) - start_epoch ))
    set_status "$name" "status" '"completed"'
    set_status "$name" "completed" "\"$(date -Iseconds)\""
    set_status "$name" "elapsed_sec" "$elapsed"
    echo ""
    echo "  ✅ COMPLETED: $name (${elapsed}s = $((elapsed / 60))m ${elapsed}s)"
  else
    local elapsed=$(( $(date +%s) - start_epoch ))
    set_status "$name" "status" '"failed"'
    set_status "$name" "elapsed_sec" "$elapsed"
    echo ""
    echo "  ❌ FAILED: $name after ${elapsed}s"
    echo "  Check output above for errors."
    return 1
  fi
}

# ── Main ──
echo "HSAP Paper Pipeline Runner"
echo "Status file: $STATUS_FILE"
echo "Re-run safely after interruption — completed tasks are skipped."
echo ""

init_status

for entry in "${TASKS[@]}"; do
  run_task "$entry"
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ALL TASKS COMPLETE"
echo "  $(date)"
echo "═══════════════════════════════════════════════════════════════"
echo ""
python3 -c "
import json
with open('$STATUS_FILE') as f: d = json.load(f)
total = sum(t.get('elapsed_sec', 0) or 0 for t in d.values())
print(f'Total wall time: {total // 3600}h {(total % 3600) // 60}m {total % 60}s')
"
