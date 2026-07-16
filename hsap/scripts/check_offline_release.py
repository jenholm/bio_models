#!/usr/bin/env python3
"""Offline release smoke test for HSAP visualization.

Checks that the standalone package has no runtime dependencies.

Usage:
    python scripts/check_offline_release.py
    python scripts/check_offline_release.py --dir hsap_visualization_release
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
RELEASE_DIR = ROOT / "hsap_visualization_release"


def check(label: str, condition: bool, errors: list):
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    if not condition:
        errors.append(label)


def main():
    parser = argparse.ArgumentParser(description="Offline release smoke test")
    parser.add_argument("--dir", type=str, default=None)
    args = parser.parse_args()

    target = Path(args.dir) if args.dir else WEB_DIR
    print(f"Checking: {target}\n")

    errors = []

    # Find HTML file (support both naming conventions)
    html_file = None
    for name in ["hsap_visual_simulation.html", "index.html"]:
        if (target / name).exists():
            html_file = target / name
            break
    check("HTML file exists", html_file is not None, errors)

    # Find JS files (support both naming conventions)
    js_dir = target / "js"
    check("js/ directory exists", js_dir.exists(), errors)

    data_js = None
    for name in ["hsap_data.js"]:
        if (js_dir / name).exists():
            data_js = js_dir / name
            break
    check("hsap_data.js exists", data_js is not None, errors)

    viz_js = None
    for name in ["hsap_visual_simulation.js", "hsap_visualization.js"]:
        if (js_dir / name).exists():
            viz_js = js_dir / name
            break
    check("visualization js exists", viz_js is not None, errors)

    # Find CSS file (support both naming conventions)
    css_dir = target / "css"
    css_file = None
    for name in ["hsap_visual_simulation.css", "hsap_visualization.css"]:
        if (css_dir / name).exists():
            css_file = css_dir / name
            break
    check("css file exists", css_file is not None, errors)

    # HTML references
    html = html_file.read_text(errors="replace") if html_file else ""
    check("HTML references hsap_data.js", "hsap_data.js" in html, errors)
    check("HTML references visualization js", "hsap_visual_simulation.js" in html or "hsap_visualization.js" in html, errors)

    # Verify load order: data before visualization
    data_pos = html.find("hsap_data.js")
    viz_pos = max(html.find("hsap_visual_simulation.js"), html.find("hsap_visualization.js"))
    check("hsap_data.js loads before visualization js", data_pos < viz_pos, errors)

    # No runtime network calls
    js_files = list(js_dir.glob("*.js")) if js_dir.exists() else []
    all_js = " ".join(f.read_text(errors="replace") for f in js_files)

    check("No fetch() calls", "fetch(" not in all_js, errors)
    check("No XMLHttpRequest", "XMLHttpRequest" not in all_js, errors)
    check("No external CDN URLs in JS", not re.search(r'https?://[^\s"\']+', all_js), errors)
    # Allow GitHub links only in About panel (informational, not runtime)
    # Find all external URLs in HTML
    all_urls = re.findall(r'https?://[^\s"\']+', html)
    # Filter out GitHub links (which are only in About panel)
    non_github_urls = [u for u in all_urls if 'github.com' not in u]
    check("No external CDN URLs in HTML (GitHub links in About panel OK)", len(non_github_urls) == 0, errors)

    # HSAP_DATA defined
    check("HSAP_DATA defined in hsap_data.js", "const HSAP_DATA" in all_js or "var HSAP_DATA" in all_js, errors)

    print(f"\n{'='*40}")
    if errors:
        print(f"RESULT: FAIL ({len(errors)} errors)")
        sys.exit(1)
    else:
        print("RESULT: PASS — offline release is valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
