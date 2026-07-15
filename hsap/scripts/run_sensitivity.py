#!/usr/bin/env python3
"""Run Sobol sensitivity analysis on key parameters."""

from pathlib import Path

from hsap.config import HSAPConfig
from hsap.sensitivity import SensitivityAnalyzer
from hsap.io import save_sensitivity_results


def main():
    out_dir = Path("results/tables")
    out_dir.mkdir(parents=True, exist_ok=True)

    config = HSAPConfig()
    analyzer = SensitivityAnalyzer(config)

    print("Running Sobol sensitivity analysis (256 samples)...")
    results = analyzer.run_sobol(n_samples=256, n_steps=200)
    save_sensitivity_results(results, str(out_dir / "sensitivity.json"))

    print("\n=== Sensitivity Results (first-order indices) ===")
    for output_name, metrics in results.items():
        print(f"\n{output_name}:")
        print(f"  {'Parameter':30s} {'S1':>8s} {'ST':>8s}")
        for param in metrics["S1"]:
            s1 = metrics["S1"][param]
            st = metrics["ST"][param]
            print(f"  {param:30s} {s1:>8.4f} {st:>8.4f}")


if __name__ == "__main__":
    main()
