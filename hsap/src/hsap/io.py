from __future__ import annotations
import json
import yaml
import pandas as pd
from pathlib import Path
from .config import HSAPConfig


def save_metrics_csv(metrics_df: pd.DataFrame, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(path, index=False)


def save_summary_json(summary: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)


def save_config_yaml(config: HSAPConfig, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(config.model_dump(), f, default_flow_style=False)


def load_config_yaml(path: str) -> HSAPConfig:
    return HSAPConfig.model_validate(yaml.safe_load(Path(path).read_text()))


def save_ga_results(results: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    serializable = {}
    for k, v in results.items():
        if k == "log":
            serializable[k] = [
                {gen_k: (float(gen_v) if isinstance(gen_v, (int, float)) else gen_v) for gen_k, gen_v in gen.items()}
                for gen in v
            ]
        else:
            serializable[k] = v
    with open(path, "w") as f:
        json.dump(serializable, f, indent=2)


def save_sensitivity_results(results: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2, default=str)
